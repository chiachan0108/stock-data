import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區]
# =============================================================================
GITHUB_USER = "chiachan0108"
GITHUB_REPO = "stock-data"

st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

# 💡 視覺系統 11.0：全面 1000 張門檻、無縫對接、4欄定版
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&family=Noto+Sans+TC:wght@300;500;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', 'Noto Sans TC', sans-serif !important; 
        background-color: #0b0f19 !important; color: #e2e8f0 !important;
    }

    .header-group { margin-top: -30px; margin-bottom: 5px; }
    .main-title { 
        font-family: 'JetBrains Mono', monospace !important; font-weight: 700; letter-spacing: -2px; 
        background: linear-gradient(90deg, #00f2ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: clamp(2.5rem, 6vw, 3.8rem); line-height: 1.2; margin: 0;
    }
    .sub-title { font-size: 1.3rem; color: #94a3b8; letter-spacing: 3px; margin-bottom: 15px; font-weight: 300; }
    
    .status-pill {
        display: inline-flex; align-items: center; background: rgba(0, 242, 255, 0.05);
        border: 1px solid rgba(0, 242, 255, 0.2); padding: 5px 15px; border-radius: 50px;
        font-size: 0.8rem; color: #00f2ff; margin-bottom: 10px;
    }
    .pulse-dot {
        height: 8px; width: 8px; background-color: #00f2ff; border-radius: 50%;
        display: inline-block; margin-right: 10px; box-shadow: 0 0 8px #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

    .section-label {
        font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: #00f2ff;
        letter-spacing: 2px; margin-top: 15px; margin-bottom: 8px; font-weight: 600; text-transform: uppercase;
    }

    div[data-testid="stSelectbox"] { margin-top: -5px !important; margin-bottom: 20px !important; }
    div[data-testid="stSelectbox"] label { display: none !important; }
    
    .stSelectbox [data-baseweb="select"] {
        background-color: #161b2a !important; border: 1px solid rgba(0, 242, 255, 0.3) !important;
        border-radius: 12px !important; height: 52px !important;
    }
    
    .stSelectbox div[data-baseweb="select"] > div {
        font-size: 1rem !important; padding-left: 15px !important; height: 50px !important;
        display: flex !important; align-items: center !important; line-height: 1 !important;
    }

    /* 4 欄強制定版 */
    .logic-grid { display: grid; gap: 15px; grid-template-columns: repeat(1, 1fr); margin-bottom: 30px; }
    @media (min-width: 1024px) { .logic-grid { grid-template-columns: repeat(4, 1fr) !important; } }

    .logic-item { 
        background: #161b22; border: 1px solid rgba(148, 163, 184, 0.15); 
        border-top: 3px solid #00f2ff; border-radius: 12px; padding: 20px; transition: 0.3s;
    }
    .logic-item:hover { background: #1c2331; transform: translateY(-3px); }
    .logic-header { display: flex; align-items: center; margin-bottom: 12px; gap: 10px; }
    .logic-icon { font-size: 1.2rem; }
    .logic-index { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00f2ff; }
    .logic-subtitle { font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .logic-desc { font-size: 0.85rem; color: #94a3b8; line-height: 1.6; }
    .highlight { color: #ffffff; font-weight: 600; background: rgba(0, 242, 255, 0.1); padding: 0 4px; border-bottom: 1px solid #00f2ff; }

    .disclaimer-box {
        background: rgba(30, 41, 59, 0.4); border-left: 4px solid #334155; padding: 15px;
        border-radius: 4px; margin: 30px 0; font-size: 0.85rem; color: #64748b;
    }

    .stButton > button {
        background: linear-gradient(90deg, #00f2ff, #0072ff) !important;
        color: white !important; border: none !important; border-radius: 8px !important; 
        font-weight: 700 !important; letter-spacing: 1px; padding: 12px 0 !important; width: 100% !important; min-height: 50px !important;
    }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False
now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
data_date = now_taipei.strftime('%Y-%m-%d') if now_taipei.hour >= 20 else (now_taipei - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# 頂部整合渲染
st.markdown(f'''
    <div class="header-group">
        <h1 class="main-title">QUANTUM SCANNER</h1>
        <div class="sub-title">台股智能量化篩選系統</div>
        <div class="status-pill">
            <span class="pulse-dot"></span>
            每日 20:00 更新資料庫 &nbsp; | &nbsp; 最後更新日：{data_date}
        </div>
        <div class="section-label">Strategy Configuration 策略選取</div>
    </div>
''', unsafe_allow_html=True)

if not st.session_state['scan_completed']:
    strategy_options = ["A. 營收動能型 (基本面優先)", "B. 股價動能型 (技術面優先)", "C. 營收、股價動能雙吻合"]
    strategy_choice = st.selectbox("量化策略模組", strategy_options, label_visibility="collapsed")
    
    st.markdown("<div class='section-label'>System Architecture 系統核心邏輯</div>", unsafe_allow_html=True)

    if "A." in strategy_choice:
        TARGET_MODE = "single_1"
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🎯</span><span class="logic-index">01/SCOPE</span></div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">鎖定台灣上市櫃<span class="highlight">電子產業</span>標的。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🌊</span><span class="logic-index">02/LIQUIDITY</span></div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均成交量需大於 <span class="highlight">1,000張</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">⚖️</span><span class="logic-index">03/LEVEL</span></div><div class="logic-subtitle">技術位階</div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">📈</span><span class="logic-index">04/TREND</span></div><div class="logic-subtitle">趨勢排列</div><div class="logic-desc"><span class="highlight">MA60 > MA240</span>，呈現多頭排列趨勢。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">👑</span><span class="logic-index">05/SCALE</span></div><div class="logic-subtitle">營收規模</div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下 <span class="highlight">5年來最高</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🔥</span><span class="logic-index">06/MOMENTUM</span></div><div class="logic-subtitle">創高動能</div><div class="logic-desc">近 6 個月內至少有單月營收創下 <span class="highlight">歷史新高</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">⚡</span><span class="logic-index">07/DYNAMICS</span></div><div class="logic-subtitle">雙重成長</div><div class="logic-desc">確保近1季 YoY > 0 且 <span class="highlight">今年累計 YoY > 0</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🏦</span><span class="logic-index">08/TRACKING</span></div><div class="logic-subtitle">法人佈局</div><div class="logic-desc">追蹤近 <span class="highlight">20 日三大法人</span> 淨買賣超張數。</div></div>
        </div>"""
    elif "B." in strategy_choice:
        TARGET_MODE = "single_2"
        # 💡 已將說明同步調整為 1,000 張
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🎯</span><span class="logic-index">01/SCOPE</span></div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">全體上市櫃，嚴格排除 <span class="highlight">ETF、權證</span> 等非普通股。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🌊</span><span class="logic-index">02/LIQUIDITY</span></div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">1,000張</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">📊</span><span class="logic-index">03/TRACKING</span></div><div class="logic-subtitle">雙週期比對</div><div class="logic-desc">股價 240 日與 20 日績效需 <span class="highlight">超越大盤同期</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🏦</span><span class="logic-index">04/SMART MONEY</span></div><div class="logic-subtitle">法人護航</div><div class="logic-desc">近 20 個交易日三大法人呈現 <span class="highlight">淨買超</span> 狀態。</div></div>
        </div>"""
    else:
        TARGET_MODE = "dual_intersection"
        logic_html = """
        <div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🧬</span><span class="logic-index">01/INTERSECTION</span></div><div class="logic-subtitle">雙引擎交集</div><div class="logic-desc">自動抓出具備 <span class="highlight">營收創高</span> 與 <span class="highlight">技術強勢</span> 的標的。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">👑</span><span class="logic-index">02/FUNDAMENTAL</span></div><div class="logic-subtitle">基本面護城河</div><div class="logic-desc">營收創 5 年新高，且近1季與 <span class="highlight">今年累計營收</span> 正成長。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">📈</span><span class="logic-index">03/TECHNICAL</span></div><div class="logic-subtitle">技術面爆發</div><div class="logic-desc">均線多頭排列，且績效皆 <span class="highlight">超越大盤同期</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🏦</span><span class="logic-index">04/SMART MONEY</span></div><div class="logic-subtitle">法人雙重認同</div><div class="logic-desc">確保近 <span class="highlight">20 日三大法人</span> 淨買超且營收正成長。</div></div>
        </div>"""
    
    st.markdown(logic_html, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🚀 啟動AI量化篩選", use_container_width=True):
            with st.status("正在執行深度運算...", expanded=True) as status:
                time.sleep(1.5)
                try:
                    url_1 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/daily_result.csv?t={int(time.time())}"
                    url_2 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/momentum_result.csv?t={int(time.time())}"
                    if TARGET_MODE == "single_1":
                        r = requests.get(url_1, timeout=10)
                        df_f = pd.read_csv(io.StringIO(r.text)) if r.status_code == 200 else pd.DataFrame()
                    elif TARGET_MODE == "single_2":
                        r = requests.get(url_2, timeout=10)
                        df_f = pd.read_csv(io.StringIO(r.text)) if r.status_code == 200 else pd.DataFrame()
                    else:
                        r1, r2 = requests.get(url_1, timeout=10), requests.get(url_2, timeout=10)
                        if r1.status_code == 200 and r2.status_code == 200:
                            df1, df2 = pd.read_csv(io.StringIO(r1.text)), pd.read_csv(io.StringIO(r2.text))
                            df_f = pd.merge(df1, df2[['股價代號', '240日報酬(%)', '20日報酬(%)', '近20日買超張數' if '近20日買超張數' in df2.columns else '近20日法人買賣超(張)']], on='股價代號', how='inner') if not df1.empty else pd.DataFrame()
                        else: df_f = pd.DataFrame()

                    if not df_f.empty:
                        df_f.index = range(1, len(df_f) + 1)
                        st.session_state['temp_df'] = df_f
                        st.session_state['selected_strategy'] = strategy_choice
                        st.session_state['scan_completed'] = True
                        st.rerun()
                    else: st.error("目前無符合標的。")
                except: st.error("連線超時。")
else:
    m1, m2, m3 = st.columns(3)
    m1.metric("🎯 符合標的", f"{len(st.session_state['temp_df'])} 檔")
    m2.metric("📅 數據基準日", str(data_date))
    m3.metric("🧠 策略模組", st.session_state['selected_strategy'].split('.')[0])
    
    st.button("🔄 重新選擇策略", on_click=lambda: st.session_state.update({"scan_completed": False}), use_container_width=True)
    st.markdown(f"### 🏆 TOP PICKS : {st.session_state['selected_strategy']}")
    
    df = st.session_state['temp_df']
    if "A." in st.session_state['selected_strategy']:
        display_cols = ["股價代號", "公司名稱", "產業別", "現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近20日法人買賣超(張數)"]
        st.dataframe(df[display_cols].style.format({"現價": "{:.2f}", "季乖離": "{:.2f}%", "年乖離": "{:.2f}%", "月營收MoM(%)": "{:.2f}%", "月營收YoY(%)": "{:.2f}%", "今年以來累積營收YoY(%)": "{:.2f}%", "近20日法人買賣超(張數)": "{:,.0f}"}), use_container_width=True)
    elif "B." in st.session_state['selected_strategy']:
        display_cols = ['股價代號', '公司名稱', '產業別', '現價', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']
        df_b = df[display_cols].rename(columns={'240日報酬(%)': '近240日報酬(%)', '20日報酬(%)': '近20日報酬(%)', '近20日法人買賣超(張)': '近20日法人買超張數'})
        st.dataframe(df_b.style.format({"現價": "{:.2f}", "近240日報酬(%)": "{:+.2f}%", "近20日報酬(%)": "{:+.2f}%", "近20日法人買超張數": "{:,.0f}"}), use_container_width=True)
    else:
        display_cols = ['股價代號', '公司名稱', '產業別', '現價', '今年以來累積營收YoY(%)', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']
        st.dataframe(df[display_cols].style.format({"現價": "{:.2f}", "今年以來累積營收YoY(%)": "{:.2f}%", "240日報酬(%)": "{:+.2f}%", "20日報酬(%)": "{:+.2f}%", "近20日法人買賣超(張)": "{:,.0f}"}), use_container_width=True)

    st.markdown('''<div class="disclaimer-box"><b>💡 免責聲明：</b>篩選結果為大數據量化得出，僅供參考不作為進出場依據，投資有風險請做好自身資金控管。</div>''', unsafe_allow_html=True)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df.to_excel(writer, index=False)
    st.download_button("📥 下載 Excel 數據報告", output.getvalue(), file_name=f"Quant_Report_{data_date}.xlsx")

st.divider(); st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
