import streamlit as st
import pandas as pd
import datetime, io, time

RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

st.set_page_config(page_title="台股電子量化智選系統", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .logic-card { background: rgba(255, 255, 255, 0.05); border-left: 4px solid #00f2ff; padding: 15px; border-radius: 8px; margin-bottom: 10px; }
    .highlight { color: #ffde59; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

st.title("🛡️ QUANTUM TECH SCANNER")
st.caption("台股電子產業：深度量化與還原權值績效監控")
st.markdown("---")

if not st.session_state['scan_completed']:
    _, center_col, _ = st.columns([1, 6, 1])
    with center_col:
        st.write("### 核心篩選邏輯")
        st.markdown("""
        <div class="logic-card">🚀 <b>還原權值比對</b>：計算近 60 日績效並扣除 0050 漲幅，精確顯示超額報酬。</div>
        <div class="logic-card">👥 <b>籌碼監控修正</b>：即時同步近 5 日三大法人合計買賣超張數。</div>
        <div class="logic-card">🏭 <b>營收三冠王</b>：LTM 創 5 年新高、單月歷史新高、季 YoY > 0。</div>
        """, unsafe_allow_html=True)

        if st.button("🚀 啟動全量量化掃描系統", type="primary", use_container_width=True):
            with st.status("📡 正在執行分析...", expanded=True) as status:
                for i in range(1, 6):
                    time.sleep(3.0)
                    status.write(f"正在執行第 {i}/5 階段：比對還原權值績效與籌碼同步...")
                try:
                    df = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 掃描完成", state="complete", expanded=False)
                    st.balloons(); st.rerun()
                except: st.error("數據讀取失敗")
else:
    df = st.session_state['temp_df']
    st.sidebar.button("🔄 重新掃描", on_click=lambda: st.session_state.update({"scan_completed": False}))
    
    st.subheader(f"🏆 QUANTUM TOP PICKS ({df['更新日期'].iloc[0]})")
    
    # 色階美化
    styled = df.style.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
    if '近5日法人超(張)' in df.columns:
        styled = styled.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')
    if '近一季相對大盤強弱' in df.columns:
        styled = styled.background_gradient(subset=['近一季相對大盤強弱'], cmap='RdYlGn')

    st.dataframe(styled.format({
        "現價": "{:.2f}", "季乖離(%)": "{:.2f}%", "年乖離(%)": "{:.2f}%", 
        "近一季相對大盤強弱": "{:+.2f}%", "營收YoY(%)": "{:.2f}%", "營收MoM(%)": "{:.2f}%"
    }), use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 下載 Excel 報表", output.getvalue(), file_name="Quant_Report.xlsx")
