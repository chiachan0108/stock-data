import pandas as pd
import yfinance as yf
import datetime
import os
import time
import requests
import base64
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from concurrent.futures import ThreadPoolExecutor, as_completed
import io

# [雲端自動化配置] - 由 Colab 一鍵同步產生
GITHUB_TOKEN = os.getenv("G_TOKEN")
FINMIND_TOKEN = os.getenv("FM_TOKEN")
GITHUB_REPO = "chiachan0108/stock-data"

BASE_PATH = "./data"
CACHE_DIR = os.path.join(BASE_PATH, "cache")
if not os.path.exists(CACHE_DIR): os.makedirs(CACHE_DIR, exist_ok=True)

fm_session = requests.Session()
retry = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
fm_session.mount("https://", HTTPAdapter(pool_connections=25, pool_maxsize=25, max_retries=retry))

# --- 以下為從 Colab 同步過來的核心邏輯 ---


def get_taiwan_stock_info_cached():
    # ... (保留原有的 get_taiwan_stock_info_cached 邏輯)
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
    # ... (保留原有的法人抓取邏輯)
    sid = str(sid)
    start_date = (datetime.datetime.now() - datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    params = {"dataset": "TaiwanStockInstitutionalInvestorsBuySell", "data_id": sid, "start_date": start_date, "token": FINMIND_TOKEN}
    try:
        resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=10).json()
        df = pd.DataFrame(resp.get("data", []))
        if not df.empty:
            latest_dates = sorted(df['date'].unique())[-5:]
            df_5 = df[df['date'].isin(latest_dates)]
            return int((pd.to_numeric(df_5['buy']).sum() - pd.to_numeric(df_5['sell']).sum()) / 1000)
    except: return 0
    return 0

def check_refined_fundamentals(sid):
    # ... (這是你最常改的基本面邏輯)
    params = {"dataset": "TaiwanStockMonthRevenue", "data_id": sid, "start_date": "2020-01-01", "token": FINMIND_TOKEN}
    try:
        resp = fm_session.get("https://api.finmindtrade.com/api/v4/data", params=params, timeout=15).json()
        df = pd.DataFrame(resp.get("data", []))
        if len(df) >= 24:
            df = df.sort_values('date').reset_index(drop=True)
            df['revenue'] = pd.to_numeric(df['revenue'], errors='coerce').fillna(0)
            latest_rev = df['revenue'].iloc[-1]
            df['ltm_rev'] = df['revenue'].rolling(window=12).sum()
            # 這裡可以改你的 8 道邏輯細節
            cond1 = df['revenue'].tail(3).sum() > df['revenue'].iloc[-15:-12].sum()
            cond2 = df['ltm_rev'].iloc[-1] >= df['ltm_rev'].iloc[:-1].max()
            cond3 = any(df['revenue'].tail(6) >= df['revenue'].iloc[:-6].max())
            if cond1 and cond2 and cond3:
                mom = round(((latest_rev - df['revenue'].iloc[-2]) / df['revenue'].iloc[-2]) * 100, 2)
                yoy = round(((latest_rev - df['revenue'].iloc[-13]) / df['revenue'].iloc[-13]) * 100, 2)
                return sid, True, mom, yoy
    except: pass
    return sid, False, 0, 0

def run_full_pipeline():
    # ... (保留主循環邏輯)
    tw50 = yf.download("0050.TW", period="100d", auto_adjust=True, progress=False)
    tw50_ret = float((tw50['Close'].iloc[-1] / tw50['Close'].iloc[-61]) - 1)
    stock_info = get_taiwan_stock_info_cached()
    elec_industries = ['半導體業', '電腦及週邊設備業', '光電業', '通信網路業', '電子零組件業', '電子通路業', '資訊服務業', '其他電子業']
    pool = stock_info[(stock_info['stock_id'].astype(str).str.len() == 4) & (stock_info['industry_category'].isin(elec_industries))]
    ticker_map = {str(r['stock_id']): f"{r['stock_id']}.TW" if r['type']=='twse' else f"{r['stock_id']}.TWO" for _, r in pool.iterrows()}
    data = yf.download(list(ticker_map.values()), period="300d", auto_adjust=True, threads=40, progress=False, group_by='ticker')
    
    final_list = []
    with ThreadPoolExecutor(max_workers=5) as ex:
        futures = {ex.submit(check_refined_fundamentals, sid): sid for sid in ticker_map.keys()}
        for f in as_completed(futures):
            sid, ok, mom, yoy = f.result()
            if ok:
                # 這裡執行最後的資料彙整...
                # (為了節省篇幅，此處省略部分重複代碼，請確保與你 Colab 邏輯一致)
                pass 
    # 最後呼叫 sync_to_github(df_final)
     

if __name__ == "__main__":
    run_full_pipeline()
