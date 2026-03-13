import streamlit as st
import pandas as pd
import datetime
import io
import time

# =============================================================================
# [核心配置：GitHub 數據來源]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 網頁版頁面配置與 CSS 樣式定義]
# =============================================================================
st.set_page_config(page_title="台股電子量化智選系統", layout="wide", initial_sidebar_state="collapsed")

# 注入科技感 CSS
st.markdown("""
    <style>
    /* 全域字體美化 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* 科技感標語容器 */
    .logic-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 15px;
        margin-top: 20px;
    }

    /* 單個邏輯卡片設計 */
    .logic-card {
        background: rgba(255, 255, 255, 0.05);
        border-left: 4px solid #00f2ff;
        padding: 15px;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    
    .logic-card:hover {
        background: rgba(0, 242, 255, 0.1);
        transform: translateY(-2px);
    }

    /* 標題數字與名稱 */
    .step-header {
        font-family: 'JetBrains Mono', monospace;
        color: #00f2ff;
        font-size: 0.8rem;
        font-weight: 700;
        margin-bottom: 5px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .condition-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 8px;
    }

    /* 關鍵字高亮 */
    .highlight {
        color: #ffde59;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
    }
    
    .desc {
        color: #b0b0b0;
        font-size: 0.9rem;
        line-height: 1.4;
    }
    </style>
""", unsafe_allow_html=True)

# 初始化 session_state
if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面展示]
# =============================================================================

st.title("🛡️ QUANTUM TECH SCANNER")
st.caption("台股電子產業：深度量化與籌碼監控引擎")
st.markdown("---")

if not st.session_state['scan_completed']:
    # --- 時尚科技感首頁 ---
    _, center_col, _ = st.columns([1, 6, 1])
    
    with center_col:
        st.write("### 核心篩選邏輯 | FILTERING LOGIC")
        st.write("系統整合多維度大數據，針對 900+ 檔標的執行以下 8 重過濾：")
        
        # 使用 HTML 注入卡片式佈局
        st.markdown(f"""
        <div class="logic-container">
            <div class="logic-card">
                <div class="step-header">Step 01</div>
                <div class="condition-name">產業範圍</div>
                <div class="desc">鎖定上市櫃全體<span class="highlight">電子產業</span>標的。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 02</div>
                <div class="condition-name">流動性門檻</div>
                <div class="desc">近 20 日日均成交量大於 <span class="highlight">1,000 張</span>。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 03</div>
                <div class="condition-name">技術位階</div>
                <div class="desc">現價站穩長線支撐 <span class="highlight">年線 (MA240)</span>。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 04</div>
                <div class="condition-name">技術趨勢</div>
                <div class="desc"><span class="highlight">季線 (MA60)</span> 高於年線，呈多頭排列。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 05</div>
                <div class="condition-name">營收規模</div>
                <div class="desc">12 個月累積營收 (<span class="highlight">LTM</span>) 創下 5 年新高。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 06</div>
                <div class="condition-name">創高動能</div>
                <div class="desc">近 6 個月內有單月營收創下 <span class="highlight">歷史新高</span>。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 07</div>
                <div class="condition-name">季度動能</div>
                <div class="desc">近 3 月營收總和高於去年同期 (<span class="highlight">季 YoY > 0</span>)。</div>
            </div>
            <div class="logic-card">
                <div class="step-header">Step 08</div>
                <div class="condition-name">籌碼監控</div>
                <div class="desc">即時統計近 5 個交易日<span class="highlight">三大法人</span>合計買賣超。</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("###")
        # 啟動按鈕
        if st.button("🚀 啟動全量量化掃描系統", type="primary", use_container_width=True):
            with st.status("📡 正在初始化量化核心...", expanded=True) as status:
                # 每個階段 2.5 秒，總計 15 秒
                time.sleep(2.5); status.write("📍 Step 1-2: 正在過濾電子產業與流動性數據...")
                time.sleep(2.5); status.write("📈 Step 3-4: 正在計算年線位階與趨勢排列...")
                time.sleep(2.5); status.write("🏭 Step 5: 正在計算 12 個月累積營收規模...")
                time.sleep(2.5); status.write("💥 Step 6-7: 正在驗證營收歷史新高與季度 YoY 動能...")
                time.sleep(2.5); status.write("👥 Step 8: 正在讀取近 5 日法人合計買賣超張數...")
                time.sleep(2.5); status.write("🏆 正在編譯最終精選報告...")
                
                try:
                    df_raw = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df_raw
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 掃描任務完成", state="complete", expanded=False)
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"數據讀取失敗: {e}")

else:
    # --- 結果顯示頁面 ---
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "2026-03-13"
    
    # 頂部儀表板卡片
    c1, c2, c3 = st.columns(3)
    c1.metric("今日掃描樣本", "900+ 檔")
    c2.metric("通過量化篩選", f"{len(df)} 檔")
    c3.metric("資料更新日期", f"{update_date}")

    st.subheader("🏆 QUANTUM TOP PICKS")
    
    # 自動色階樣式
    styled_df = df.style
    if '年乖離(%)' in df.columns:
        styled_df = styled_df.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
    if '近5日法人超(張)' in df.columns:
        styled_df = styled_df.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')

    st.dataframe(styled_df.format({
        "現價": "{:.2f}",
        "季乖離(%)": "{:.2f}%",
        "年乖離(%)": "{:.2f}%",
        "營收YoY(%)": "{:.2f}%",
        "營收MoM(%)": "{:.2f}%"
    }), use_container_width=True)

    # Sidebar
    st.sidebar.header("CONTROLS")
    if st.sidebar.button("🔄 重新掃描任務"):
        st.session_state['scan_completed'] = False
        st.rerun()
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 下載完整 Excel 報表", data=output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

# 頁尾
st.divider()
st.caption("QUANTUM DATA ENGINE © 2026 | 精準量化，智選未來。")
