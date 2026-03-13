import streamlit as st
import pandas as pd
import datetime, io, time

# =============================================================================
# [配置區]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 頁面配置與 高階簡約 CSS]
# =============================================================================
st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #0e1117;
        color: #e0e0e0;
    }

    .main-title {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        letter-spacing: -1px;
        color: #ffffff;
    }

    /* 8道邏輯獨立卡片 */
    .logic-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 12px;
        margin-bottom: 25px;
    }

    .logic-item {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(0, 242, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.4s cubic-bezier(0.165, 0.84, 0.44, 1);
    }

    .logic-item:hover {
        background: rgba(0, 242, 255, 0.05);
        border-color: rgba(0, 242, 255, 0.5);
        transform: translateY(-5px);
    }

    .logic-index {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #00f2ff;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .logic-title {
        font-size: 1rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 10px;
    }

    .logic-desc {
        font-size: 0.85rem;
        color: #888888;
        line-height: 1.5;
    }

    .highlight { color: #00f2ff; font-weight: 600; }
    
    /* 進度條文字美化 */
    .stProgress > div > div > div > div { background-image: linear-gradient(to right, #00f2ff, #0072ff); }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面設計]
# =============================================================================

st.markdown('<h1 class="main-title">🛡️ QUANTUM SCANNER</h1>', unsafe_allow_html=True)
st.caption("台股電子全產業：深度量化過濾與進度即時監控引擎")
st.markdown("---")

if not st.session_state['scan_completed']:
    # --- 8 道邏輯展示區 ---
    st.markdown("### 系統核心邏輯 | SYSTEM ARCHITECTURE")
    
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item">
            <div class="logic-index">01 / SCOPE</div>
            <div class="logic-title">產業範圍</div>
            <div class="logic-desc">鎖定上市櫃全體<span class="highlight">電子產業</span>，排除權證與非典型標的。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">02 / LIQUIDITY</div>
            <div class="logic-title">流動性門檻</div>
            <div class="logic-desc">近 20 日日均成交量需大於 <span class="highlight">1,000張</span>。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">03 / LEVEL</div>
            <div class="logic-title">技術位階</div>
            <div class="logic-desc">現價必須站穩長線生命線 <span class="highlight">MA240</span> 之上。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">04 / TREND</div>
            <div class="logic-title">趨勢排列</div>
            <div class="logic-desc"><span class="highlight">季線 (MA60)</span> 高於年線，確保多頭排列發散。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">05 / SCALE</div>
            <div class="logic-title">營收規模</div>
            <div class="logic-desc">12 個月累積營收 (<span class="highlight">LTM</span>) 創下 5 年來新高。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">06 / MOMENTUM</div>
            <div class="logic-title">創高爆發力</div>
            <div class="logic-desc">近 6 個月內至少有單月營收創下 <span class="highlight">歷史新高</span>紀錄。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">07 / QUARTERLY</div>
            <div class="logic-title">季度動能</div>
            <div class="logic-desc">近 3 個月營收總和高於去年同期，確保 <span class="highlight">季 YoY > 0</span>。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">08 / TRACKING</div>
            <div class="logic-title">籌碼與對標</div>
            <div class="logic-desc">同步近 5 日<span class="highlight">法人數據</span>並執行還原權值 0050 績效對比。</div>
        </div>
    </div>
    """
    st.markdown(logic_html, unsafe_allow_html=True)

    # 啟動按鈕
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🚀 啟動深度量化分析任務", type="primary", use_container_width=True):
            
            # --- 百分比進度條實作 ---
            progress_bar = st.progress(0, text="📡 正在初始化數據終端...")
            
            with st.status("正在執行深度分析...", expanded=True) as status:
                process_steps = [
                    (15, "🔍 正在過濾電子產業流動性標的..."),
                    (30, "📈 正在計算技術面位階 (MA240, MA60)..."),
                    (50, "🏭 正在分析 LTM 營收與歷史新高紀錄..."),
                    (70, "👥 正在同步三大法人籌碼分點資料..."),
                    (90, "⚖️ 正在執行 0050 還原權值績效對標..."),
                    (100, "🏆 正在編譯最終精選報告...")
                ]
                
                for percent, step_text in process_steps:
                    time.sleep(2.5) # 總計 15 秒儀式
                    progress_bar.progress(percent, text=step_text)
                    status.write(step_text)
                
                try:
                    df = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 分析任務已結案", state="complete", expanded=False)
                    st.balloons()
                    st.rerun()
                except:
                    st.error("數據同步失敗")

else:
    # --- 結果頁面 ---
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else datetime.date.today()
    
    # 頂部儀表板
    m1, m2, m3 = st.columns(3)
    m1.metric("掃描總數", "900+ 檔")
    m2.metric("符合門檻", f"{len(df)} 檔")
    m3.metric("更新日期", str(update_date))
    
    st.sidebar.button("🔄 重新啟動掃描", on_click=lambda: st.session_state.update({"scan_completed": False}))
    
    st.subheader("🏆 QUANTUM TOP PICKS")
    
    # 色階渲染
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
    st.sidebar.download_button("📥 下載 Excel 報告", output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

st.divider()
st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
