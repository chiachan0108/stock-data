import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區]
# =============================================================================
GITHUB_USER = "chiachan0108"
GITHUB_REPO = "stock-data"

st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; background-color: #0e1117; color: #e0e0e0; }
    .main-title { font-family: 'JetBrains Mono', monospace; font-weight: 700; letter-spacing: -1.5px; color: #ffffff; font-size: 3rem; margin-bottom: 5px; }
    .update-note { font-size: 0.95rem; color: #888888; background: rgba(255, 255, 255, 0.03); padding: 8px 15px; border-radius: 50px; display: inline-block; margin-bottom: 25px; border: 1px solid rgba(255, 255, 255, 0.05); }
    .logic-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 30px; }
    .logic-item { background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(0, 242, 255, 0.15); border-radius: 14px; padding: 24px; }
    .logic-index { font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #00f2ff; font-weight: 700; margin-bottom: 12px; }
    .logic-subtitle { font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .logic-desc { font-size: 0.95rem; color: #a0a0a0; line-height: 1.6; }
    .highlight { color: #00f2ff; font-weight: 700; }
    .stProgress > div > div > div > div { background: linear-gradient(to right, #00f2ff, #0072ff); height: 8px; }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False

st.markdown('<h1 class="main-title">🛡️ QUANTUM SCANNER</h1>', unsafe_allow_html=True)
st.markdown('<div class="update-note">🕒 數據公告：每日 20:00 定時更新資料庫</div>', unsafe_allow_html=True)

# --- 策略選擇器 ---
strategy_choice = st.selectbox("📂 請選擇量化策略模組", ["營收動能成長型(基本面優先)", "趨勢動能強勢型(技術面優先)"])

if strategy_choice == "營收動能成長型(基本面優先)":
    TARGET_CSV = "daily_result.csv"
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item"><div class="logic-index">01 / SCOPE</div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">鎖定台灣全體上市櫃<span class="highlight">電子產業</span>標的。</div></div>
        <div class="logic-item"><div class="logic-index">02 / LIQUIDITY</div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">1,000張</span>。</div></div>
        <div class="logic-item"><div class="logic-index">03 / LEVEL</div><div class="logic-subtitle">技術位階</div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div></div>
        <div class="logic-item"><div class="logic-index">04 / TREND</div><div class="logic-subtitle">趨勢排列</div><div class="logic-desc"><span class="highlight">MA60 > MA240</span>，呈現中長線多頭排列。</div></div>
        <div class="logic-item"><div class="logic-index">05 / SCALE</div><div class="logic-subtitle">營收規模</div><div class="logic-desc">近12個月累積營收 (LTM) 創下5年來最高紀錄。</div></div>
        <div class="logic-item"><div class="logic-index">06 / MOMENTUM</div><div class="logic-subtitle">創高動能</div><div class="logic-desc">近6個月內至少有1個月以上的營收創下 <span class="highlight">歷史新高</span>。</div></div>
        <div class="logic-item"><div class="logic-index">07 / DYNAMICS</div><div class="logic-subtitle">季度動能</div><div class="logic-desc">確保 <span class="highlight">近1季YoY > 0</span>，營運動能持續擴張。</div></div>
        <div class="logic-item"><div class="logic-index">08 / TRACKING</div><div class="logic-subtitle">相對強弱判定</div><div class="logic-desc">更新三大法人籌碼並 <span class="highlight">判定相對大盤強弱</span> 。</div></div>
    </div>
    """
else:
    TARGET_CSV = "momentum_result.csv"
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item"><div class="logic-index">01 / SCOPE</div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">全體上市櫃，<span class="highlight">嚴格排除 ETF、ETN、權證</span>等非普通股。</div></div>
        <div class="logic-item"><div class="logic-index">02 / LIQUIDITY</div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">500張</span>。</div></div>
        <div class="logic-item"><div class="logic-index">03 / TRACKING</div><div class="logic-subtitle">雙週期大盤對標</div><div class="logic-desc">近 240 日與 20 日績效 <span class="highlight">皆需超越 0050</span> (還原權值)。</div></div>
        <div class="logic-item"><div class="logic-index">04 / SMART MONEY</div><div class="logic-subtitle">法人籌碼護航</div><div class="logic-desc">近 20 個交易日三大法人買賣超 <span class="highlight">大於 0 張</span>。</div></div>
    </div>
    """

st.markdown("---")

if not st.session_state['scan_completed']:
    st.markdown("### 系統核心邏輯 | SYSTEM ARCHITECTURE")
    st.markdown(logic_html, unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        display_name = strategy_choice.split('(')[0]
        if st.button(f"🚀 啟動【{display_name}】即時篩選系統", type="primary", use_container_width=True):
            p_bar = st.progress(0, text="📡 正在連接量化數據終端...")
            with st.status("正在執行深度過濾與運算...", expanded=True) as status:
                # 💡 設定 5 個步驟，每個步驟 3 秒，總計 15 秒
                steps = [
                    (20, "🔍 正在初始化全體上市櫃數據終端..."),
                    (40, "📈 執行多維度技術指標過濾與位階判定..."),
                    (60, "🏭 檢索基本面營收規模與成長加速度數據..."),
                    (80, "👥 同步三大法人近 20 日籌碼分布狀態..."),
                    (100, "🏆 執行 0050 相對強弱判定並產出最終報告...")
                ]
                for p, txt in steps:
                    time.sleep(3.0)  # 每個步驟精確停頓 3 秒
                    p_bar.progress(p, text=txt)
                    status.write(txt)
                
                try:
                    RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/{TARGET_CSV}"
                    r = requests.get(f"{RAW_URL}?t={int(time.time())}", timeout=10)
                    if r.status_code == 200:
                        st.session_state['temp_df'] = pd.read_csv(io.StringIO(r.text), on_bad_lines='skip')
                        st.session_state['scan_completed'] = True
                        status.update(label="✅ 篩選完成", state="complete", expanded=False)
                        st.balloons(); st.rerun()
                    else: st.error(f"數據讀取失敗，請確認資料庫狀態。")
                except Exception: st.error("連線超時，請稍後再試。")
else:
    df = st.session_state['temp_df']
    tz_delta = datetime.timedelta(hours=8)
    now_taipei = datetime.datetime.utcnow() + tz_delta
    
    if not df.empty and '更新日期' in df.columns: 
        update_date = df['更新日期'].iloc[0]
    else: 
        update_date = now_taipei.strftime('%Y-%m-%d') if now_taipei.hour >= 20 else (now_taipei - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    m1, m2, m3 = st.columns(3)
    m1.metric("今日掃描樣本", "900+ 檔" if "營收動能" in strategy_choice else "1700+ 檔")
    m2.metric("符合門檻標的", f"{len(df)} 檔")
    m3.metric("數據最後更新", str(update_date))
    
    st.button("🔄 重新選擇策略", on_click=lambda: st.session_state.update({"scan_completed": False}))
    st.subheader(f"🏆 TOP PICKS")
    
    if not df.empty:
        styled = df.style
        if strategy_choice == "營收動能成長型(基本面優先)":
            styled = styled.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r') \
                           .background_gradient(subset=['近5日法人買賣超(張數)'], cmap='Greens') \
                           .background_gradient(subset=['近一季相對大盤強弱'], cmap='RdYlGn')
            st.dataframe(styled.format({
                "現價": "{:.2f}", "季乖離(%)": "{:.2f}%", "年乖離(%)": "{:.2f}%", 
                "近一季相對大盤強弱": "{:+.2f}%", "營收YoY(%)": "{:.2f}%", "營收MoM(%)": "{:.2f}%"
            }, na_rep="-"), use_container_width=True)
        else:
            styled = styled.background_gradient(subset=['近20日法人買賣超(張)'], cmap='Greens') \
                           .background_gradient(subset=['240日報酬(%)'], cmap='RdYlGn') \
                           .background_gradient(subset=['20日報酬(%)'], cmap='RdYlGn')
            st.dataframe(styled.format({
                "現價": "{:.2f}", "240日報酬(%)": "{:+.2f}%", "20日報酬(%)": "{:+.2f}%", 
                "近20日法人買賣超(張)": "{:,.0f}"
            }, na_rep="-"), use_container_width=True)
    else:
        st.warning("目前暫無符合條件的選股結果。")
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: 
        df.to_excel(writer, index=False)
    st.download_button("📥 下載 Excel 完整報告", output.getvalue(), file_name=f"{TARGET_CSV.split('.')[0]}_{update_date}.xlsx")

st.divider(); st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
