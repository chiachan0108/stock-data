import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區]
# =============================================================================
GITHUB_USER = "chiachan0108"
GITHUB_REPO = "stock-data"

st.set_page_config(page_title="QUANTUM TECH SCANNER | 台股智能量化篩選", layout="wide", initial_sidebar_state="collapsed")

# 💡 全新進化：極致質感 CSS 視覺系統
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+TC:wght@100;300;400;500;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', 'Noto Sans TC', sans-serif; 
        background: radial-gradient(circle at top right, #1a202c, #0b0f19);
        color: #e2e8f0;
    }
    
    /* 標題動畫與排版 */
    .title-wrapper {
        margin-top: 20px;
        margin-bottom: 5px;
    }
    .main-title { 
        font-family: 'JetBrains Mono', monospace; 
        font-weight: 700; 
        letter-spacing: -2px; 
        background: linear-gradient(135deg, #00f2ff 0%, #0072ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 4rem; 
        line-height: 1.1;
    }
    .sub-title {
        font-family: 'Noto Sans TC', sans-serif;
        font-weight: 300;
        font-size: 1.5rem;
        color: #94a3b8;
        letter-spacing: 4px;
        margin-top: 5px;
        display: block;
    }

    /* 動態狀態標籤 */
    .status-pill {
        display: inline-flex;
        align-items: center;
        background: rgba(0, 242, 255, 0.05);
        border: 1px solid rgba(0, 242, 255, 0.2);
        padding: 5px 15px;
        border-radius: 50px;
        font-size: 0.85rem;
        color: #00f2ff;
        margin-bottom: 30px;
        margin-top: 20px;
    }
    .pulse-dot {
        height: 8px;
        width: 8px;
        background-color: #00f2ff;
        border-radius: 50%;
        display: inline-block;
        margin-right: 10px;
        box-shadow: 0 0 12px #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 242, 255, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 10px rgba(0, 242, 255, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(0, 242, 255, 0); }
    }

    /* 💡 策略選擇區優化 */
    .config-container {
        background: rgba(30, 41, 59, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 20px;
        padding: 30px;
        margin-bottom: 40px;
        box-shadow: inset 0 1px 1px rgba(255,255,255,0.05);
    }
    .section-header {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.9rem;
        letter-spacing: 2px;
        color: #64748b;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
    }
    .section-header::after {
        content: "";
        flex: 1;
        height: 1px;
        background: rgba(100, 116, 139, 0.2);
        margin-left: 20px;
    }

    /* 邏輯卡片設計 */
    .logic-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
    .logic-item { 
        background: rgba(255, 255, 255, 0.02); 
        border: 1px solid rgba(148, 163, 184, 0.1); 
        border-radius: 16px; padding: 26px; 
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    .logic-item:hover { 
        transform: translateY(-8px); 
        border-color: rgba(0, 242, 255, 0.5); 
        background: rgba(30, 41, 59, 0.6);
        box-shadow: 0 20px 40px -20px rgba(0,0,0,0.5);
    }
    .logic-index { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #00f2ff; margin-bottom: 12px; opacity: 0.8; }
    .logic-subtitle { font-size: 1.25rem; font-weight: 700; color: #ffffff; margin-bottom: 12px; }
    .logic-desc { font-size: 0.95rem; color: #94a3b8; line-height: 1.7; }
    .highlight { color: #ffffff; font-weight: 600; background: rgba(0, 242, 255, 0.1); padding: 2px 6px; border-radius: 4px; border-bottom: 1px solid #00f2ff; }

    /* 免責聲明 */
    .disclaimer-box {
        background: rgba(15, 23, 42, 0.8);
        border-left: 3px solid #334155;
        padding: 20px;
        border-radius: 4px;
        margin: 40px 0;
        font-size: 0.9rem;
        color: #64748b;
    }

    /* 調整 Streamlit 預設樣式 */
    .stSelectbox [data-baseweb="select"] {
        background-color: rgba(15, 23, 42, 0.5);
        border-radius: 12px;
        border: 1px solid rgba(0, 242, 255, 0.2);
        transition: all 0.3s;
    }
    .stSelectbox [data-baseweb="select"]:hover {
        border-color: #00f2ff;
        box-shadow: 0 0 10px rgba(0, 242, 255, 0.1);
    }
    </style>
""", unsafe_allow_html=True)

# --- 核心狀態與動態日期計算 ---
if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False

now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
data_date = now_taipei.strftime('%Y-%m-%d') if now_taipei.hour >= 20 else (now_taipei - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# --- 頂部標題區 ---
st.markdown('''
    <div class="title-wrapper">
        <h1 class="main-title">QUANTUM SCANNER</h1>
        <span class="sub-title">台股智能量化篩選</span>
    </div>
''', unsafe_allow_html=True)

st.markdown(f'''
    <div class="status-pill">
        <span class="pulse-dot"></span>
        每日 20:00 更新資料庫 &nbsp; | &nbsp; 最後更新日：{data_date}
    </div>
''', unsafe_allow_html=True)

# --- 策略選取區塊 ---
if not st.session_state['scan_completed']:
    st.markdown('<div class="config-container">', unsafe_allow_html=True)
    st.markdown("<div class='section-header'>STRATEGY CONFIGURATION 策略選取</div>", unsafe_allow_html=True)
    
    strategy_options = ["A. 營收動能型 (基本面優先)", "B. 股價動能型 (技術面優先)", "C. 營收、股價動能雙吻合"]
    strategy_choice = st.selectbox("量化策略模組", strategy_options, label_visibility="collapsed")
    
    # 根據選擇顯示邏輯
    if "A." in strategy_choice:
        TARGET_MODE = "single_1"
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-index">01 / SCOPE</div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">鎖定台灣全體上市櫃<span class="highlight">電子產業</span>標的。</div></div>
            <div class="logic-item"><div class="logic-index">02 / LIQUIDITY</div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">1,000張</span>。</div></div>
            <div class="logic-item"><div class="logic-index">03 / LEVEL</div><div class="logic-subtitle">技術位階</div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div></div>
            <div class="logic-item"><div class="logic-index">04 / TREND</div><div class="logic-subtitle">趨勢排列</div><div class="logic-desc"><span class="highlight">MA60 > MA240</span>，呈現多頭排列。</div></div>
            <div class="logic-item"><div class="logic-index">05 / SCALE</div><div class="logic-subtitle">營收規模</div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下 <span class="highlight">5年來最高紀錄</span>。</div></div>
            <div class="logic-item"><div class="logic-index">06 / MOMENTUM</div><div class="logic-subtitle">創高動能</div><div class="logic-desc">近 6 個月內至少有單月營收創下 <span class="highlight">歷史新高</span>。</div></div>
            <div class="logic-item"><div class="logic-index">07 / DYNAMICS</div><div class="logic-subtitle">雙重成長</div><div class="logic-desc">確保近1季 YoY > 0 且 <span class="highlight">今年累計 YoY > 0</span>。</div></div>
            <div class="logic-item"><div class="logic-index">08 / TRACKING</div><div class="logic-subtitle">法人佈局</div><div class="logic-desc">追蹤近 <span class="highlight">20 日三大法人</span> 買賣超張數。</div></div>
        </div>"""
    elif "B." in strategy_choice:
        TARGET_MODE = "single_2"
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-index">01 / SCOPE</div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">全體上市櫃公司，嚴格排除 <span class="highlight">ETF、ETN、權證</span> 等非普通股。</div></div>
            <div class="logic-item"><div class="logic-index">02 / LIQUIDITY</div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">500張</span>。</div></div>
            <div class="logic-item"><div class="logic-index">03 / TRACKING</div><div class="logic-subtitle">雙週期比對</div><div class="logic-desc">股價近 240 日與 20 日績效皆需 <span class="highlight">超越大盤同期績效</span>。</div></div>
            <div class="logic-item"><div class="logic-index">04 / SMART MONEY</div><div class="logic-subtitle">法人護航</div><div class="logic-desc">近 20 個交易日三大法人呈現 <span class="highlight">淨買超</span>。</div></div>
        </div>"""
    else:
        TARGET_MODE = "dual_intersection"
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-index">01 / INTERSECTION</div><div class="logic-subtitle">雙引擎交集</div><div class="logic-desc">系統自動比對，抓出同時具備 <span class="highlight">營收創高動能</span> 與 <span class="highlight">技術面強勢</span> 的標的。</div></div>
            <div class="logic-item"><div class="logic-index">02 / FUNDAMENTAL</div><div class="logic-subtitle">基本面護城河</div><div class="logic-desc">營收創 5 年新高，且近1季與 <span class="highlight">今年累計營收</span> 皆為正成長。</div></div>
            <div class="logic-item"><div class="logic-index">03 / TECHNICAL</div><div class="logic-subtitle">技術面爆發</div><div class="logic-desc">均線多頭排列，且長短天期績效皆 <span class="highlight">超越大盤同期</span>。</div></div>
            <div class="logic-item"><div class="logic-index">04 / SMART MONEY</div><div class="logic-subtitle">法人雙重認同</div><div class="logic-desc">確保近 <span class="highlight">20 日三大法人</span> 淨買超且營收為正成長。</div></div>
        </div>"""
    
    st.markdown("<div style='margin-top:30px;'></div>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>SYSTEM ARCHITECTURE 系統核心邏輯</div>", unsafe_allow_html=True)
    st.markdown(logic_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        display_name = strategy_choice.split('. ')[1].split('(')[0].strip()
        if st.button(f"🚀 啟動【{display_name}】AI量化篩選系統", type="primary", use_container_width=True):
            p_bar = st.progress(0, text="📡 正在連接數據終端...")
            with st.status("正在執行深度運算...", expanded=True) as status:
                steps = [(20, "🔍 初始化數據..."), (40, "📈 技術過濾..."), (60, "🏭 營收判定..."), (80, "👥 同步籌碼..."), (100, "🏆 產出報告...")]
                for p, txt in steps:
                    time.sleep(2.5) 
                    p_bar.progress(p, text=txt); status.write(txt)
                try:
                    url_1 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/daily_result.csv?t={int(time.time())}"
                    url_2 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/momentum_result.csv?t={int(time.time())}"
                    if TARGET_MODE == "single_1":
                        r = requests.get(url_1, timeout=10)
                        df_final = pd.read_csv(io.StringIO(r.text)) if r.status_code == 200 else pd.DataFrame()
                    elif TARGET_MODE == "single_2":
                        r = requests.get(url_2, timeout=10)
                        df_final = pd.read_csv(io.StringIO(r.text)) if r.status_code == 200 else pd.DataFrame()
                    else:
                        r1, r2 = requests.get(url_1, timeout=10), requests.get(url_2, timeout=10)
                        if r1.status_code == 200 and r2.status_code == 200:
                            df1, df2 = pd.read_csv(io.StringIO(r1.text)), pd.read_csv(io.StringIO(r2.text))
                            df_final = pd.merge(df1, df2[['股價代號', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']], on='股價代號', how='inner') if not df1.empty else pd.DataFrame()
                        else: df_final = pd.DataFrame()

                    if not df_final.empty:
                        df_final.index = range(1, len(df_final) + 1)
                        st.session_state['temp_df'] = df_final
                        st.session_state['selected_strategy'] = strategy_choice
                        st.session_state['scan_completed'] = True
                        status.update(label="✅ 篩選完成", state="complete", expanded=False); st.rerun()
                    else: st.error("目前無符合標的。")
                except Exception: st.error("連線超時，請稍後再試。")
else:
    # 顯示結果頁面
    df = st.session_state['temp_df']
    strategy_choice = st.session_state['selected_strategy']
    
    m1, m2, m3 = st.columns(3)
    m1.metric("📌 掃描樣本池", "極致交集" if "C." in strategy_choice else ("900+ 檔" if "A." in strategy_choice else "1700+ 檔"))
    m2.metric("🎯 符合門檻標的", f"{len(df)} 檔")
    m3.metric("🕒 數據基準日", str(data_date))
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔄 重新選擇策略 (返回主選單)", on_click=lambda: st.session_state.update({"scan_completed": False}), type="primary", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"### 🏆 TOP PICKS : {strategy_choice}")
    
    if not df.empty:
        if "A." in strategy_choice:
            display_cols = ["股價代號", "公司名稱", "產業別", "現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近20日法人買賣超(張數)"]
            st.dataframe(df[display_cols].style.format({"現價": "{:.2f}", "季乖離": "{:.2f}%", "年乖離": "{:.2f}%", "月營收MoM(%)": "{:.2f}%", "月營收YoY(%)": "{:.2f}%", "今年以來累積營收YoY(%)": "{:.2f}%", "近20日法人買賣超(張數)": "{:,.0f}"}), use_container_width=True)
        elif "B." in strategy_choice:
            display_cols = ['股價代號', '公司名稱', '產業別', '現價', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']
            df_b = df[display_cols].rename(columns={'240日報酬(%)': '近240日報酬(%)', '20日報酬(%)': '近20日報酬(%)', '近20日法人買賣超(張)': '近20日法人買超張數'})
            st.dataframe(df_b.style.format({"現價": "{:.2f}", "近240日報酬(%)": "{:+.2f}%", "近20日報酬(%)": "{:+.2f}%", "近20日法人買超張數": "{:,.0f}"}), use_container_width=True)
        else:
            display_cols = ['股價代號', '公司名稱', '產業別', '現價', '今年以來累積營收YoY(%)', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']
            st.dataframe(df[display_cols].style.format({"現價": "{:.2f}", "今年以來累積營收YoY(%)": "{:.2f}%", "240日報酬(%)": "{:+.2f}%", "20日報酬(%)": "{:+.2f}%", "近20日法人買賣超(張)": "{:,.0f}"}), use_container_width=True)

        st.markdown('''<div class="disclaimer-box"><b>💡 免責聲明：</b><br>篩選結果為大數據資料庫量化得出，僅供參考不作為進出場依據，投資有風險請做好自身資金控管。</div>''', unsafe_allow_html=True)
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df.to_excel(writer, index=False)
        st.download_button("📥 下載完整數據報告 (Excel)", output.getvalue(), file_name=f"Quant_Report_{data_date}.xlsx", type="primary")
    else:
        st.info("💡 目前暫無符合標的。")

st.divider(); st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
