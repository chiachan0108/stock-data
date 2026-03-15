import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區]
# =============================================================================
GITHUB_USER = "chiachan0108"
GITHUB_REPO = "stock-data"

st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

# 視覺優化 CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&family=Noto+Sans+TC:wght@400;500;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Inter', 'Noto Sans TC', sans-serif; 
        background: linear-gradient(135deg, #090B10 0%, #111520 100%);
        color: #e2e8f0;
    }
    .main-title { 
        font-family: 'JetBrains Mono', monospace; 
        font-weight: 700; 
        letter-spacing: -1.5px; 
        background: linear-gradient(90deg, #00f2ff, #0072ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3.5rem; 
        margin-bottom: 0px; 
        text-shadow: 0px 4px 20px rgba(0, 242, 255, 0.2);
    }
    .update-note { 
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem; 
        color: #94a3b8; 
        background: rgba(15, 23, 42, 0.6); 
        padding: 6px 14px; 
        border-radius: 4px; 
        border-left: 3px solid #00f2ff;
        display: inline-block; 
        margin-bottom: 35px;
        margin-top: 10px;
    }
    .logic-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; margin-bottom: 40px; }
    .logic-item { 
        background: rgba(30, 41, 59, 0.4); 
        border: 1px solid rgba(148, 163, 184, 0.1); 
        border-radius: 12px; 
        padding: 24px; 
        backdrop-filter: blur(10px);
        transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
    }
    .logic-item:hover { transform: translateY(-5px); box-shadow: 0 10px 30px -10px rgba(0, 242, 255, 0.15); border-color: rgba(0, 242, 255, 0.4); }
    .logic-index { font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #00f2ff; font-weight: 600; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 1px; }
    .logic-subtitle { font-size: 1.2rem; font-weight: 700; color: #f8fafc; margin-bottom: 12px; }
    .logic-desc { font-size: 0.95rem; color: #cbd5e1; line-height: 1.6; }
    .highlight { color: #ffffff; font-weight: 600; background: rgba(0, 242, 255, 0.15); padding: 2px 6px; border-radius: 4px; border-bottom: 1px solid #00f2ff; }
    .stProgress > div > div > div > div { background: linear-gradient(90deg, #00f2ff, #0072ff); }
    .stButton > button { border-radius: 8px; font-weight: 600; letter-spacing: 0.5px; }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False

st.markdown('<h1 class="main-title">QUANTUM SCANNER</h1>', unsafe_allow_html=True)
st.markdown('<div class="update-note">SYS.STATUS: ONLINE | DATA_SYNC: DAILY 20:00 CST</div>', unsafe_allow_html=True)

# --- 策略選擇器 ---
strategy_options = [
    "A. 營收動能型 (基本面優先)", 
    "B. 股價動能型 (技術面優先)",
    "C. 營收、股價動能雙吻合"
]
st.markdown("### ⚙️ STRATEGY CONFIGURATION")

# 下拉選單在掃描完成後會鎖定
strategy_choice = st.selectbox(
    "請選擇量化策略模組", 
    strategy_options, 
    label_visibility="collapsed",
    disabled=st.session_state['scan_completed']
)

if strategy_choice == "A. 營收動能型 (基本面優先)":
    TARGET_MODE = "single_1"
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item"><div class="logic-index">01 / SCOPE</div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">鎖定台灣全體上市櫃<span class="highlight">電子產業</span>標的。</div></div>
        <div class="logic-item"><div class="logic-index">02 / LIQUIDITY</div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">1,000張</span>。</div></div>
        <div class="logic-item"><div class="logic-index">03 / LEVEL</div><div class="logic-subtitle">技術位階</div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div></div>
        <div class="logic-item"><div class="logic-index">04 / TREND</div><div class="logic-subtitle">趨勢排列</div><div class="logic-desc"><span class="highlight">MA60 > MA240</span>，呈現中長線多頭排列。</div></div>
        <div class="logic-item"><div class="logic-index">05 / SCALE</div><div class="logic-subtitle">營收規模</div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下 <span class="highlight">5年來最高紀錄</span>。</div></div>
        <div class="logic-item"><div class="logic-index">06 / MOMENTUM</div><div class="logic-subtitle">創高動能</div><div class="logic-desc">近 6 個月內至少有單月營收創下 <span class="highlight">歷史新高</span>。</div></div>
        <div class="logic-item"><div class="logic-index">07 / DYNAMICS</div><div class="logic-subtitle">雙重成長動能</div><div class="logic-desc">確保近1季 YoY > 0 且 <span class="highlight">今年累計 YoY > 0</span>。</div></div>
        <div class="logic-item"><div class="logic-index">08 / TRACKING</div><div class="logic-subtitle">法人佈局</div><div class="logic-desc">追蹤近 <span class="highlight">20 日三大法人</span> 買賣超張數。</div></div>
    </div>
    """
elif strategy_choice == "B. 股價動能型 (技術面優先)":
    TARGET_MODE = "single_2"
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item"><div class="logic-index">01 / SCOPE</div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">全體上市櫃公司，嚴格排除 <span class="highlight">ETF、ETN、權證</span> 等非普通股。</div></div>
        <div class="logic-item"><div class="logic-index">02 / LIQUIDITY</div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">500張</span>。</div></div>
        <div class="logic-item"><div class="logic-index">03 / TRACKING</div><div class="logic-subtitle">雙週期績效比對</div><div class="logic-desc">股價近 240 日與 20 日績效皆需 <span class="highlight">超越大盤同期績效</span>。</div></div>
        <div class="logic-item"><div class="logic-index">04 / SMART MONEY</div><div class="logic-subtitle">法人籌碼護航</div><div class="logic-desc">近 20 個交易日三大法人呈現 <span class="highlight">淨買超</span>。</div></div>
    </div>
    """
else:
    TARGET_MODE = "dual_intersection"
    # 💡 依照您的需求更新 C 選項 04 的文字敘述
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item"><div class="logic-index">01 / INTERSECTION</div><div class="logic-subtitle">雙引擎交集</div><div class="logic-desc">系統自動比對，抓出同時具備 <span class="highlight">營收創高動能</span> 與 <span class="highlight">技術面強勢</span> 的標的。</div></div>
        <div class="logic-item"><div class="logic-index">02 / FUNDAMENTAL</div><div class="logic-subtitle">基本面護城河</div><div class="logic-desc">營收創 5 年新高，且近1季與 <span class="highlight">今年累計營收</span> 皆為正成長。</div></div>
        <div class="logic-item"><div class="logic-index">03 / TECHNICAL</div><div class="logic-subtitle">技術面爆發力</div><div class="logic-desc">均線多頭排列，且長短天期績效皆 <span class="highlight">超越大盤同期</span>。</div></div>
        <div class="logic-item"><div class="logic-index">04 / SMART MONEY</div><div class="logic-subtitle">法人雙重認同</div><div class="logic-desc">近 <span class="highlight">20 日三大法人</span> 淨買超且營收為正成長。</div></div>
    </div>
    """

st.markdown("---")

if not st.session_state['scan_completed']:
    st.markdown("### 🧠 SYSTEM ARCHITECTURE")
    st.markdown(logic_html, unsafe_allow_html=True)
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        display_name = strategy_choice.split('. ')[1].split('(')[0].strip()
        if st.button(f"🚀 啟動【{display_name}】AI量化篩選系統", type="primary", use_container_width=True):
            p_bar = st.progress(0, text="📡 正在連接量化數據終端...")
            with st.status("正在執行深度過濾與運算...", expanded=True) as status:
                steps = [(20, "🔍 初始化全體上市櫃數據..."), (40, "📈 執行多維度技術指標過濾..."), (60, "🏭 檢索營收規模與成長數據..."), (80, "👥 同步三大法人籌碼分布..."), (100, "🏆 產出最終精選報告...")]
                for p, txt in steps:
                    time.sleep(3.0) 
                    p_bar.progress(p, text=txt)
                    status.write(txt)
                
                try:
                    url_1 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/daily_result.csv?t={int(time.time())}"
                    url_2 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/momentum_result.csv?t={int(time.time())}"
                    if TARGET_MODE == "single_1":
                        r = requests.get(url_1, timeout=10)
                        df_final = pd.read_csv(io.StringIO(r.text), on_bad_lines='skip') if r.status_code == 200 else pd.DataFrame()
                    elif TARGET_MODE == "single_2":
                        r = requests.get(url_2, timeout=10)
                        df_final = pd.read_csv(io.StringIO(r.text), on_bad_lines='skip') if r.status_code == 200 else pd.DataFrame()
                    else:
                        r1, r2 = requests.get(url_1, timeout=10), requests.get(url_2, timeout=10)
                        if r1.status_code == 200 and r2.status_code == 200:
                            df1, df2 = pd.read_csv(io.StringIO(r1.text)), pd.read_csv(io.StringIO(r2.text))
                            if not df1.empty and not df2.empty:
                                df1['股價代號'], df2['股價代號'] = df1['股價代號'].astype(str), df2['股價代號'].astype(str)
                                df_final = pd.merge(df1, df2[['股價代號', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']], on='股價代號', how='inner')
                            else: df_final = pd.DataFrame()
                        else: df_final = pd.DataFrame()

                    if not df_final.empty:
                        # 索引從 1 開始
                        df_final.index = range(1, len(df_final) + 1)
                        st.session_state['temp_df'] = df_final
                        st.session_state['scan_completed'] = True
                        status.update(label="✅ 篩選完成", state="complete", expanded=False)
                        st.rerun()
                    else: st.error("目前無符合標的或數據讀取失敗。")
                except Exception: st.error("連線超時，請稍後再試。")
else:
    df = st.session_state['temp_df']
    now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
    update_date = now_taipei.strftime('%Y-%m-%d')
    
    m1, m2, m3 = st.columns(3)
    if "C." in strategy_choice: sample_text = "極致交集比對"
    elif "A." in strategy_choice: sample_text = "900+ 檔"
    else: sample_text = "1700+ 檔"
    
    m1.metric("📌 掃描樣本池", sample_text)
    m2.metric("🎯 符合門檻標的", f"{len(df)} 檔")
    m3.metric("🕒 數據基準日", str(update_date))
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("🔄 重新選擇策略 (返回主選單)", on_click=lambda: st.session_state.update({"scan_completed": False}), type="primary", use_container_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🏆 QUANTUM TOP PICKS")
    
    if not df.empty:
        if "A." in strategy_choice:
            display_cols_a = ["股價代號", "公司名稱", "產業別", "現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近20日法人買賣超(張數)"]
            st.dataframe(df[display_cols_a].style.format({
                "現價": "{:.2f}", "季乖離": "{:.2f}%", "年乖離": "{:.2f}%", 
                "月營收MoM(%)": "{:.2f}%", "月營收YoY(%)": "{:.2f}%", "今年以來累積營收YoY(%)": "{:.2f}%",
                "近20日法人買賣超(張數)": "{:,.0f}"
            }, na_rep="-"), use_container_width=True)
            
        elif "B." in strategy_choice:
            display_cols_b = ['股價代號', '公司名稱', '產業別', '現價', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']
            df_b_display = df[display_cols_b].rename(columns={'240日報酬(%)': '近240日報酬(%)', '20日報酬(%)': '近20日報酬(%)', '近20日法人買賣超(張)': '近20日法人買超張數'})
            st.dataframe(df_b_display.style.format({"現價": "{:.2f}", "近240日報酬(%)": "{:+.2f}%", "近20日報酬(%)": "{:+.2f}%", "近20日法人買超張數": "{:,.0f}"}, na_rep="-"), use_container_width=True)
            
        else:
            display_cols_c = ['股價代號', '公司名稱', '產業別', '現價', '今年以來累積營收YoY(%)', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']
            st.dataframe(df[display_cols_c].style.format({"現價": "{:.2f}", "今年以來累積營收YoY(%)": "{:.2f}%", "240日報酬(%)": "{:+.2f}%", "20日報酬(%)": "{:+.2f}%", "近20日法人買賣超(張)": "{:,.0f}"}, na_rep="-"), use_container_width=True)
    else:
        st.info("💡 目前暫無同時符合兩大嚴苛策略的交集標的，請靜候市場輪動。")
    
    if not df.empty:
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer: df.to_excel(writer, index=False)
        st.download_button("📥 下載完整數據報告 (Excel)", output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx", type="primary")

st.divider(); st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
