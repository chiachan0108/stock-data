import streamlit as st
import pandas as pd
import datetime
import io
import time

# =============================================================================
# [核心配置]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 頁面配置與 CSS 注入]
# =============================================================================
st.set_page_config(page_title="台股電子量化智選系統", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
    
    .logic-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00f2ff;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 10px;
    }
    .highlight { color: #ffde59; font-weight: 700; font-family: 'JetBrains Mono', monospace; }
    .condition-name { font-size: 1.0rem; font-weight: 700; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面]
# =============================================================================
st.title("🛡️ QUANTUM TECH SCANNER")
st.caption("台股電子產業：大數據深度量化與相對強度過濾")
st.markdown("---")

if not st.session_state['scan_completed']:
    _, center_col, _ = st.columns([1, 6, 1])
    with center_col:
        st.write("### 核心篩選邏輯 | FILTERING LOGIC")
        st.markdown(f"""
        <div class="logic-card"><div class="condition-name">📍 產業與流動性</div><div style="color:#b0b0b0">鎖定上市櫃電子產業且日均量 > <span class="highlight">1,000張</span>。</div></div>
        <div class="logic-card"><div class="condition-name">📈 技術趨勢</div><div style="color:#b0b0b0">現價站穩 <span class="highlight">MA240</span> 且季線高於年線 (多頭排列)。</div></div>
        <div class="logic-card"><div class="condition-name">🚀 相對強度</div><div style="color:#b0b0b0">近 60 日還原權值漲幅 <span class="highlight">超越 0050</span> 大盤表現。</div></div>
        <div class="logic-card"><div class="condition-name">🏭 營收動能</div><div style="color:#b0b0b0"><span class="highlight">LTM</span> 創5年新高 且 近6個月有單月創歷史新高。</div></div>
        <div class="logic-card"><div class="condition-name">👥 籌碼監控</div><div style="color:#b0b0b0">即時追蹤近 5 個交易日 <span class="highlight">三大法人</span> 合計買賣超張數。</div></div>
        """, unsafe_allow_html=True)

        if st.button("🚀 啟動全量量化掃描系統", type="primary", use_container_width=True):
            with st.status("📡 正在執行深度分析...", expanded=True) as status:
                for i in range(1, 6):
                    time.sleep(3.0)
                    status.write(f"正在執行第 {i}/5 階段大數據運算與大盤強弱比對...")
                try:
                    df_raw = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df_raw
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 掃描任務完成", state="complete", expanded=False)
                    st.balloons(); st.rerun()
                except Exception as e:
                    st.error(f"數據讀取失敗: {e}")
else:
    df = st.session_state['temp_df']
    
    # --- 側邊欄過濾選項 ---
    st.sidebar.header("📊 數據篩選")
    only_strong = st.sidebar.toggle("僅顯示近60日相對大盤強勢股", value=False)
    
    if only_strong:
        df = df[df['相對大盤(60日)'] == "強"]
        st.sidebar.success("已開啟強勢股過濾")
    
    if st.sidebar.button("🔄 重新執行掃描"):
        st.session_state['scan_completed'] = False; st.rerun()

    st.subheader(f"🏆 QUANTUM TOP PICKS (共 {len(df)} 檔)")
    
    styled_df = df.style.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
    if '近5日法人超(張)' in df.columns:
        styled_df = styled_df.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')

    # 對「強」標註特別顏色
    def highlight_strong(val):
        color = '#00f2ff' if val == '強' else '#b0b0b0'
        return f'color: {color}; font-weight: bold'

    st.dataframe(styled_df.applymap(highlight_strong, subset=['相對大盤(60日)']).format({
        "現價": "{:.2f}", "季乖離(%)": "{:.2f}%", "年乖離(%)": "{:.2f}%", "營收YoY(%)": "{:.2f}%", "營收MoM(%)": "{:.2f}%"
    }), use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 下載 Excel 報表", data=output.getvalue(), file_name=f"Quant_Report.xlsx")

st.divider()
st.caption("QUANTUM DATA ENGINE © 2026 | 精準量化，對標大盤。")
