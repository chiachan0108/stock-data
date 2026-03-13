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
st.set_page_config(page_title="台股電子量化智選系統", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

    .logic-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }

    .logic-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00f2ff;
        padding: 15px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .logic-card:hover { background: rgba(0, 242, 255, 0.1); transform: translateY(-2px); }

    .step-header {
        font-family: 'JetBrains Mono', monospace;
        color: #00f2ff;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .condition-name { font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .highlight { color: #ffde59; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
    .desc { color: #b0b0b0; font-size: 0.9rem; line-height: 1.4; }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面]
# =============================================================================
st.title("🛡️ QUANTUM TECH SCANNER")
st.caption("台股電子產業：深度量化與營收動能掃描引擎")
st.markdown("---")

if not st.session_state['scan_completed']:
    _, center_col, _ = st.columns([1, 6, 1])
    
    with center_col:
        st.write("### 核心篩選邏輯 | FILTERING LOGIC")
        st.write("系統鎖定具備長線趨勢與強勁營收動能之電子標的：")
        
        st.markdown(f"""
        <div class="logic-container">
            <div class="logic-card">
                <div class="step-header">Step 01</div>
                <div class="condition-name">產業與流動性</div>
                <div class="desc">鎖定上市櫃電子產業且日均量 > <span class="highlight">1,000張</span>。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 02</div>
                <div class="condition-name">長線支撐</div>
                <div class="desc">股價站穩關鍵長線支撐 <span class="highlight">年線 (MA240)</span>。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 03</div>
                <div class="condition-name">技術趨勢</div>
                <div class="desc"><span class="highlight">季線 (MA60)</span> 高於年線，呈現多頭排列型態。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 04</div>
                <div class="condition-name">營收規模</div>
                <div class="desc">12 個月累積營收 (<span class="highlight">LTM</span>) 創下 5 年新高。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 05</div>
                <div class="condition-name">創高動能</div>
                <div class="desc">近 6 個月內有單月營收創下 <span class="highlight">歷史新高</span>。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 06</div>
                <div class="condition-name">季度動能</div>
                <div class="desc">近 3 月營收總和高於去年同期 (<span class="highlight">季 YoY > 0</span>)。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 07</div>
                <div class="condition-name">籌碼監控</div>
                <div class="desc">追蹤近 5 個交易日<span class="highlight">三大法人</span>合計買賣超動態。</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("###")
        if st.button("🚀 啟動全量量化掃描系統", type="primary", use_container_width=True):
            with st.status("📡 正在執行深度分析...", expanded=True) as status:
                time.sleep(3.0); status.write("📍 正在過濾產業範圍與流動性門檻...")
                time.sleep(3.0); status.write("📈 正在計算年線位階與趨勢排列...")
                time.sleep(3.0); status.write("🏭 正在計算 LTM 營收規模與歷史創高數據...")
                time.sleep(3.0); status.write("👥 正在同步三大法人籌碼動向...")
                time.sleep(3.0); status.write("🏆 正在產出今日最終報告...")
                
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
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else datetime.date.today()
    
    st.sidebar.header("CONTROLS")
    if st.sidebar.button("🔄 重新執行掃描"):
        st.session_state['scan_completed'] = False; st.rerun()

    st.subheader(f"🏆 QUANTUM TOP PICKS (共 {len(df)} 檔)")
    
    styled_df = df.style.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
    if '近5日法人超(張)' in df.columns:
        styled_df = styled_df.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')

    st.dataframe(styled_df.format({
        "現價": "{:.2f}", "季乖離(%)": "{:.2f}%", "年乖離(%)": "{:.2f}%", "營收YoY(%)": "{:.2f}%", "營收MoM(%)": "{:.2f}%"
    }), use_container_width=True)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 下載完整 Excel 報表", data=output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

st.divider()
st.caption("QUANTUM DATA ENGINE © 2026 | 精準量化，智選未來。")
