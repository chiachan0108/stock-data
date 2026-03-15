import pandas as pd
import yfinance as yf
import datetime, os, time, requests, base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed

GITHUB_TOKEN = os.getenv("G_TOKEN")
FINMIND_TOKEN_1 = os.getenv("FM_TOKEN_1")
FINMIND_TOKEN_2 = os.getenv("FM_TOKEN_2")
GITHUB_REPO = "chiachan0108/stock-data"

BASE_PATH = "./data"
CACHE_DIR = os.path.join(BASE_PATH, "cache")
if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR, exist_ok=True)

fm_session = requests.Session()
retry = Retry(total=4, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
fm_session.mount("https://", HTTPAdapter(pool_connections=25, pool_maxsize=25, max_retries=retry))

def get_pure_taiwan_stocks(token):
    cache_path = os.path.join(CACHE_DIR, "TaiwanStockInfo_Global.csv")
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) / (24 * 3600) < 30:
        df = pd.read_csv(cache_path, dtype={'stock_id': str})
    else:
        params = {"dataset": "TaiwanStockInfo", "token": token}
        try:
            resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=15).json()
            if resp.get("msg") == "success":
                df = pd.DataFrame(resp.get("data", []))
                df.to_csv(cache_path, index=False)
            else: return pd.DataFrame()
        except: return pd.DataFrame()
    
    df = df[df['stock_id'].astype(str).str.isnumeric()]
    exclude_keywords = ['ETF', 'ETN', '存託憑證', '受益證券']
    df_pure = df[
        (df['stock_id'].astype(str).str.len() == 4) & 
        (~df['industry_category'].isin(exclude_keywords)) &
        (df['type'].isin(['twse', 'tpex']))
    ]
    return df_pure

def get_institutional_net_buy(sid, token, days, force_zero=False):
    sid = str(sid)
    # 💡 修正 UTC 警告
    today_str = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
    cache_path = os.path.join(CACHE_DIR, f"{sid}_inst{days}d_{today_str}.csv")
    if os.path.exists(cache_path):
        df = pd.read_csv(cache_path)
    else:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=days+15)).strftime('%Y-%m-%d')
        params = {"dataset": "TaiwanStockInstitutionalInvestorsBuySell", "data_id": sid, "start_date": start_date, "token": token}
        try:
            resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=10).json()
            df = pd.DataFrame(resp.get("data", []))
            if not df.empty: df.to_csv(cache_path, index=False)
        except: return 0
    if isinstance(df, pd.DataFrame) and not df.empty and 'buy' in df.columns:
        latest_dates = sorted(df['date'].unique())[-days:]
        df_target = df[df['date'].isin(latest_dates)]
        return int((pd.to_numeric(df_target['buy']).sum() - pd.to_numeric(df_target['sell']).sum()) / 1000)
    return 0

def check_refined_fundamentals(sid, token):
    sid = str(sid)
    cache_path = os.path.join(CACHE_DIR, f"{sid}_rev.csv")
    df = None
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) / (24 * 3600) < 15:
        try: df = pd.read_csv(cache_path)
        except: pass
    if df is None:
        params = {"dataset": "TaiwanStockMonthRevenue", "data_id": sid, "start_date": "2020-01-01", "token": token}
        try:
            resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=15).json()
            if resp.get("msg") == "success":
                df = pd.DataFrame(resp.get("data", [])); df.to_csv(cache_path, index=False)
            else: return sid, False, 0, 0, 0
        except: return sid, False, 0, 0, 0
    
    if isinstance(df, pd.DataFrame) and 'revenue' in df.columns and len(df) >= 24:
        df = df.sort_values('date').reset_index(drop=True)
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
        
        latest_date = pd.to_datetime(df['date'].iloc[-1])
        latest_year, latest_month = latest_date.year, latest_date.month
        latest_rev = df['revenue'].iloc[-1]
        
        mom = round(((latest_rev - df['revenue'].iloc[-2]) / df['revenue'].iloc[-2]) * 100, 2) if df['revenue'].iloc[-2] > 0 else 0
        yoy = round(((latest_rev - df['revenue'].iloc[-13]) / df['revenue'].iloc[-13]) * 100, 2) if df['revenue'].iloc[-13] > 0 else 0
        
        df['year'] = pd.to_datetime(df['date']).dt.year
        df['month'] = pd.to_datetime(df['date']).dt.month
        current_ytd = df[(df['year'] == latest_year) & (df['month'] <= latest_month)]['revenue'].sum()
        last_ytd = df[(df['year'] == latest_year - 1) & (df['month'] <= latest_month)]['revenue'].sum()
        ytd_yoy = round(((current_ytd - last_ytd) / last_ytd) * 100, 2) if last_ytd > 0 else 0
        
        df['ltm_rev'] = df['revenue'].rolling(window=12).sum()
        cond1 = df['revenue'].tail(3).sum() > df['revenue'].iloc[-15:-12].sum()
        cond2 = df['ltm_rev'].iloc[-1] >= df['ltm_rev'].iloc[:-1].max()
        cond3 = any(df['revenue'].tail(6) >= df['revenue'].iloc[:-6].max())
        
        if cond1 and cond2 and cond3: return sid, True, mom, yoy, ytd_yoy
    return sid, False, 0, 0, 0

def sync_to_github_file(df, filename):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    csv_content = df.to_csv(index=False)
    resp = requests.get(url, headers=headers)
    sha = resp.json().get('sha') if resp.status_code == 200 else None
    payload = {"message": f"🤖 更新 {filename}: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", 
               "content": base64.b64encode(csv_content.encode()).decode()}
    if sha: payload["sha"] = sha
    try:
        put_resp = requests.put(url, headers=headers, json=payload, timeout=20)
        if put_resp.status_code in [200, 201]: print(f"✅ {filename} 同步成功！")
        else: print(f"❌ {filename} 同步失敗: {put_resp.text}")
    except: print(f"❌ {filename} 同步超時。")

def run_full_pipeline():
    # 💡 修正 UTC 警告
    today_str = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)).strftime('%Y-%m-%d')
    print(f"🔍 啟動今日 ({today_str}) 雙軌量化掃描任務...")
    
    print("📈 下載 0050 基準資料...")
    tw50 = yf.download("0050.TW", period="350d", auto_adjust=True, progress=False)
    
    # 💡 修正 pandas float 警告：確保取得單一數值
    tw50_close = tw50['Close'].squeeze()
    tw50_ret_60 = float(tw50_close.iloc[-1] / tw50_close.iloc[-61] - 1)
    tw50_ret_240 = float(tw50_close.iloc[-1] / tw50_close.iloc[-240] - 1)
    tw50_ret_20 = float(tw50_close.iloc[-1] / tw50_close.iloc[-20] - 1)

    print("📊 獲取股票清單與歷史數據...")
    pool_all = get_pure_taiwan_stocks(FINMIND_TOKEN_1)
    ticker_map_all = {str(r['stock_id']): f"{r['stock_id']}.TW" if r['type']=='twse' else f"{r['stock_id']}.TWO" for _, r in pool_all.iterrows()}
    
    all_tickers = [t for t in ticker_map_all.values() if t not in DELISTED_BLACKLIST]

    price_cache_file = os.path.join(CACHE_DIR, f"yf_daily_prices_{today_str}.pkl")
    
    if os.path.exists(price_cache_file) and not FORCE_RELOAD:
        print(f"⚡ 發現今日 ({today_str}) 的股價快取檔案，直接載入以節省時間！")
        data = pd.read_pickle(price_cache_file)
    else:
        print(f"📡 準備分批下載 {len(all_tickers)} 檔標的歷史股價...")
        batch_size = 300  
        data_list = []
        for i in range(0, len(all_tickers), batch_size):
            batch = all_tickers[i:i + batch_size]
            print(f"📥 正在下載第 {i} 到 {min(i+batch_size, len(all_tickers))} 檔...")
            try:
                # 💡 移除 session 參數，讓 yfinance 自行處理 curl_cffi 防護
                batch_data = yf.download(batch, period="350d", auto_adjust=True, threads=15, progress=False, group_by='ticker')
                data_list.append(batch_data)
                time.sleep(2.5) 
            except Exception as e:
                print(f"⚠️ 批次下載失敗: {e}")
        
        if not data_list:
            print("❌ 所有批次下載皆失敗，終止執行。")
            return
            
        data = pd.concat(data_list, axis=1)
        data.to_pickle(price_cache_file)
        print("💾 今日股價資料已備份至雲端快取。")

    elec_industries = ['半導體業', '電腦及週邊設備業', '光電業', '通信網路業', '電子零組件業', '電子通路業', '資訊服務業', '其他電子業']
    pool_elec = pool_all[pool_all['industry_category'].isin(elec_industries)]
    elec_sids = pool_elec['stock_id'].astype(str).tolist()

    # ==========================================
    # 🛡️ 策略 1：營收動能型
    # ==========================================
    print("\n🛡️ 正在執行【策略 1：營收動能型】...")
    tech_candidates_1, metrics_1 = [], {}
    all_columns = data.columns.get_level_values(0).unique()
    
    for sid, full_ticker in ticker_map_all.items():
        if sid not in elec_sids or full_ticker not in all_columns: continue
        try:
            df = data[full_ticker].ffill().dropna()
            if len(df) < 241: continue
            p, ma60, ma240, vol = float(df['Close'].iloc[-1]), float(df['Close'].tail(60).mean()), float(df['Close'].tail(240).mean()), float(df['Volume'].tail(20).mean())
            if vol >= 1000000 and p > ma240 and ma60 > ma240:
                stock_ret = float((df['Close'].iloc[-1] / df['Close'].iloc[-61]) - 1)
                relative_ret = round((stock_ret - tw50_ret_60) * 100, 2)
                tech_candidates_1.append(sid)
                metrics_1[sid] = {"現價": p, "季乖離": round(((p-ma60)/ma60)*100, 2), "年乖離": round(((p-ma240)/ma240)*100, 2), "近一季相對大盤強弱": relative_ret}
        except: continue

    final_list_1 = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(check_refined_fundamentals, sid, FINMIND_TOKEN_1): sid for sid in tech_candidates_1}
        for f in as_completed(futures):
            sid, ok, mom, yoy, ytd_yoy = f.result()
            if ok and sid in metrics_1:
                chip_net = get_institutional_net_buy(sid, FINMIND_TOKEN_1, 5)
                row = pool_all[pool_all['stock_id'].astype(str) == sid].iloc[0]
                final_list_1.append({
                    "更新日期": today_str, "股價代號": sid, "公司名稱": row['stock_name'], "產業別": row['industry_category'],
                    "現價": round(metrics_1[sid]["現價"], 2), "季乖離": metrics_1[sid]["季乖離"], "年乖離": metrics_1[sid]["年乖離"],
                    "月營收MoM(%)": mom, "月營收YoY(%)": yoy, "今年以來累積營收YoY(%)": ytd_yoy,
                    "近5日法人買賣超(張數)": chip_net 
                })
    
    if final_list_1:
        df_quantum = pd.DataFrame(final_list_1)
        ordered_cols = ["更新日期", "股價代號", "公司名稱", "產業別", "現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近一季相對大盤強弱", "近5日法人買賣超(張數)"]
        existing_cols = [c for c in ordered_cols if c in df_quantum.columns]
        df_quantum = df_quantum[existing_cols].sort_values(by="今年以來累積營收YoY(%)", ascending=False)
    else:
        df_quantum = pd.DataFrame(columns=["更新日期", "股價代號", "公司名稱", "產業別", "現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近5日法人買賣超(張數)"])
    
    # ==========================================
    # 🚀 策略 2：股價動能型
    # ==========================================
    print("\n🚀 正在執行【策略 2：股價動能型】...")
    tech_candidates_2 = []
    for sid, full_ticker in ticker_map_all.items():
        if full_ticker not in all_columns: continue
        try:
            df = data[full_ticker].ffill().dropna()
            if len(df) < 240: continue
            vol_20_lots = float(df['Volume'].tail(20).mean()) / 1000
            if vol_20_lots <= 500: continue
            ret_240 = float((df['Close'].iloc[-1] / df['Close'].iloc[-240]) - 1)
            ret_20 = float((df['Close'].iloc[-1] / df['Close'].iloc[-20]) - 1)
            if ret_240 > tw50_ret_240 and ret_20 > tw50_ret_20:
                tech_candidates_2.append({"股價代號": sid, "現價": round(df['Close'].iloc[-1], 2), "20日均量(張)": int(vol_20_lots), "240日報酬(%)": round(ret_240 * 100, 2), "20日報酬(%)": round(ret_20 * 100, 2)})
        except: continue

    final_list_2 = []
    for item in tech_candidates_2:
        sid = item["股價代號"]
        net_buy = get_institutional_net_buy(sid, FINMIND_TOKEN_2, 20)
        if net_buy > 0:
            row = pool_all[pool_all['stock_id'].astype(str) == sid].iloc[0]
            item.update({"更新日期": today_str, "公司名稱": row['stock_name'], "產業別": row['industry_category'], "近20日法人買賣超(張)": net_buy})
            final_list_2.append(item)
            
    df_momentum = pd.DataFrame(final_list_2).sort_values(by="近20日法人買賣超(張)", ascending=False) if final_list_2 else pd.DataFrame(columns=["股價代號"])

    print(f"\n✅ 任務完成！營收型: {len(df_quantum)} 檔, 股價型: {len(df_momentum)} 檔")
    sync_to_github_file(df_quantum, "daily_result.csv")
    sync_to_github_file(df_momentum, "momentum_result.csv")


if __name__ == "__main__":
    run_full_pipeline()
