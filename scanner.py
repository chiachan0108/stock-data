import pandas as pd
import yfinance as yf
import datetime
import os
import time
import requests
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import io

# =============================================================================
# [核心配置區]
# =============================================================================
GITHUB_TOKEN = os.getenv("G_TOKEN")
GITHUB_REPO = "chiachan0108/stock-data"
FINMIND_TOKEN = os.getenv("FM_TOKEN")

# 雲端執行路徑設定
BASE_PATH = "./data"
CACHE_DIR = os.path.join(BASE_PATH, "cache")
DAILY_DIR = os.path.join(BASE_PATH, "daily_reports")

for d in [CACHE_DIR, DAILY_DIR]:
    if not os.path.exists(d): os.makedirs(d, exist_ok=True)

fm_session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
fm_session.mount("https://", HTTPAdapter(pool_connections=25, pool_maxsize=25, max_retries=retry))

def get_taiwan_stock_info_cached():
    cache_path = os.path.join(CACHE_DIR, "TaiwanStockInfo_Global.csv")
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) / (24 * 3600) < 30:
        return pd.read_csv(cache_path, dtype={'stock_id': str})
    params = {"dataset": "TaiwanStockInfo", "token": FINMIND_TOKEN}
    try:
        resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params).json()
        if resp.get("msg") == "success":
            df = pd.DataFrame(resp.get("data", []))
            df.to_csv(cache_path, index=False); return df
    except: pass
    return pd.DataFrame()

def get_institutional_net_buy_5d(sid):
    sid = str(sid)
    today_str = datetime.date.today().strftime('%Y-%m-%d')
    cache_path = os.path.join(CACHE_DIR, f"{sid}_inst_{today_str}.csv")
    if os.path.exists(cache_path):
        df = pd.read_csv(cache_path)
    else:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        params = {"dataset": "TaiwanStockInstitutionalInvestorsBuySell", "data_id": sid, "start_date": start_date, "token": FINMIND_TOKEN}
        try:
            resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=10).json()
            df = pd.DataFrame(resp.get("data", []))
            if not df.empty: df.to_csv(cache_path, index=False)
        except: return 0
    if isinstance(df, pd.DataFrame) and not df.empty and 'buy' in df.columns:
        latest_dates = sorted(df['date'].unique())[-5:]
        df_5 = df[df['date'].isin(latest_dates)]
        return int((pd.to_numeric(df_5['buy']).sum() - pd.to_numeric(df_5['sell']).sum()) / 1000)
    return 0

def check_refined_fundamentals(sid):
    sid = str(sid)
    cache_path = os.path.join(CACHE_DIR, f"{sid}_rev.csv")
    df = None
    if os.path.exists(cache_path) and (time.time() - os.path.getmtime(cache_path)) / (24 * 3600) < 15:
        try: df = pd.read_csv(cache_path)
        except: pass
    if df is None:
        params = {"dataset": "TaiwanStockMonthRevenue", "data_id": sid, "start_date": "2020-01-01", "token": FINMIND_TOKEN}
        try:
            resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=15).json()
            if resp.get("msg") == "success":
                df = pd.DataFrame(resp.get("data", [])); df.to_csv(cache_path, index=False)
            else: return sid, False, 0, 0
        except: return sid, False, 0, 0
    if isinstance(df, pd.DataFrame) and 'revenue' in df.columns and len(df) >= 24:
        df = df.sort_values('date').reset_index(drop=True)
        df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
        latest_rev = df['revenue'].iloc[-1]
        mom = round(((latest_rev - df['revenue'].iloc[-2]) / df['revenue'].iloc[-2]) * 100, 2) if df['revenue'].iloc[-2] > 0 else 0
        yoy = round(((latest_rev - df['revenue'].iloc[-13]) / df['revenue'].iloc[-13]) * 100, 2) if df['revenue'].iloc[-13] > 0 else 0
        df['ltm_rev'] = df['revenue'].rolling(window=12).sum()
        if (df['revenue'].tail(3).sum() > df['revenue'].iloc[-15:-12].sum()) and \
           (df['ltm_rev'].iloc[-1] >= df['ltm_rev'].iloc[:-1].max()) and \
           any(df['revenue'].tail(6) >= df['revenue'].iloc[:-6].max()):
            return sid, True, mom, yoy
    return sid, False, 0, 0

def sync_to_github(df):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/daily_result.csv"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    csv_content = df.to_csv(index=False)
    resp = requests.get(url, headers=headers)
    sha = resp.json().get('sha') if resp.status_code == 200 else None
    payload = {
        "message": f"🤖 [Auto] 更新量化數據: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "content": base64.b64encode(csv_content.encode()).decode()
    }
    if sha: payload["sha"] = sha
    requests.put(url, headers=headers, json=payload)

def run_full_pipeline():
    tw50 = yf.download("0050.TW", period="100d", auto_adjust=True, progress=False)
    tw50_ret = float((tw50['Close'].iloc[-1] / tw50['Close'].iloc[-61]) - 1)
    stock_info = get_taiwan_stock_info_cached()
    elec_industries = ['半導體業', '電腦及週邊設備業', '光電業', '通信網路業', '電子零組件業', '電子通路業', '資訊服務業', '其他電子業']
    pool = stock_info[(stock_info['stock_id'].astype(str).str.len() == 4) & (stock_info['industry_category'].isin(elec_industries))]
    ticker_map = {str(r['stock_id']): f"{r['stock_id']}.TW" if r['type']=='twse' else f"{r['stock_id']}.TWO" for _, r in pool.iterrows()}
    
    data = yf.download(list(ticker_map.values()), period="300d", auto_adjust=True, threads=40, progress=False, group_by='ticker')
    tech_candidates, metrics = [], {}
    all_columns = data.columns.get_level_values(0).unique()
    for sid, full_ticker in ticker_map.items():
        if full_ticker not in all_columns: continue
        try:
            df = data[full_ticker].ffill().dropna()
            if len(df) < 241: continue
            p, ma60, ma240, vol = float(df['Close'].iloc[-1]), float(df['Close'].tail(60).mean()), float(df['Close'].tail(240).mean()), float(df['Volume'].tail(20).mean())
            stock_ret = float((df['Close'].iloc[-1] / df['Close'].iloc[-61]) - 1)
            if vol >= 1000000 and p > ma240 and ma60 > ma240:
                tech_candidates.append(sid)
                metrics[sid] = {"現價": p, "季乖離": round(((p-ma60)/ma60)*100, 2), "年乖離": round(((p-ma240)/ma240)*100, 2), "近一季相對大盤強弱": round((stock_ret - tw50_ret) * 100, 2)}
        except: continue

    final_list = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(check_refined_fundamentals, sid): sid for sid in tech_candidates}
        for f in as_completed(futures):
            sid, ok, mom, yoy = f.result()
            if ok:
                chip_net = get_institutional_net_buy_5d(sid)
                row = pool[pool['stock_id'].astype(str) == sid].iloc[0]
                final_list.append({
                    "更新日期": datetime.date.today().strftime('%Y-%m-%d'), "代號": sid, "名稱": row['stock_name'], "產業": row['industry_category'],
                    "現價": round(metrics[sid]["現價"], 2), "季乖離(%)": metrics[sid]["季乖離"], "年乖離(%)": metrics[sid]["年乖離"],
                    "近一季相對大盤強弱": metrics[sid]["近一季相對大盤強弱"], "營收MoM(%)": mom, "營收YoY(%)": yoy,
                    "近5日三大法人買賣超(張數)": chip_net
                })

    df_final = pd.DataFrame(final_list if final_list else [], columns=["更新日期", "代號", "名稱", "產業", "現價", "季乖離(%)", "年乖離(%)", "近一季相對大盤強弱", "營收MoM(%)", "營收YoY(%)", "近5日三大法人買賣超(張數)"])
    sync_to_github(df_final)

if __name__ == "__main__":
    run_full_pipeline()
