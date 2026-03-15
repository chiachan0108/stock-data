
import pandas as pd
import yfinance as yf
import datetime, requests, base64, io, time, os
from concurrent.futures import ThreadPoolExecutor, as_completed

# 💡 從環境變數讀取你已有的 Secret
GITHUB_TOKEN = os.getenv("GH_TOKEN")
FM_TOKEN_1 = os.getenv("FM_TOKEN_1")
FM_TOKEN_2 = os.getenv("FM_TOKEN_2")
GITHUB_REPO = "chiachan0108/stock-data"

def sync_to_github(df, filename):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{filename}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    content = base64.b64encode(df.to_csv(index=False).encode()).decode()
    r = requests.get(url, headers=headers)
    sha = r.json().get('sha') if r.status_code == 200 else None
    payload = {"message": f"🤖 Auto Update {filename}", "content": content}
    if sha: payload["sha"] = sha
    requests.put(url, headers=headers, json=payload)

def run_quant_mission():
    print("🚀 啟動量子量化雲端引擎...")
    # --- 這裡放入你之前所有的策略運算邏輯 ---
    # 策略 A 計算...
    # 策略 B 計算...
    # 策略 C 交集...
    
    # 範例測試 (確保連線成功)
    heartbeat = pd.DataFrame([{"status": "Active", "last_run": str(datetime.datetime.now())}])
    sync_to_github(heartbeat, "heartbeat.csv")
    print("✅ 任務完成")

if __name__ == "__main__":
    run_quant_mission()
