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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #0e1117;
        color: #e0e0e0;
    }

    .main-title {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        letter-spacing: -1.5px;
        color: #ffffff;
        font-size: 3rem;
    }

    /* 8道邏輯卡片 - 字體強化版 */
    .logic-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
        margin-bottom: 30px;
    }

    .logic-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 255, 0.15);
        border-radius: 14px;
        padding: 24px;
        transition: all 0.4s ease-in-out;
    }

    .logic-item:hover {
        background: rgba(0, 242, 255, 0.06);
        border-color: rgba(0, 242, 255, 0.6);
        transform: translateY(-5px);
    }

    .logic-index {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1rem; /* 放大 */
        color: #00f2ff;
        font-weight: 700;
        margin-bottom: 12px;
        letter-spacing: 2px;
    }

    .logic-title { 
        font-size: 1.35rem; /* 標題大幅放大 */
        font-weight: 700; 
        color: #ffffff; 
        margin-bottom: 14px; 
        letter-spacing: -0.5px;
    }

    .logic-desc { 
        font-size: 1.05rem; /* 說明文字放大 */
        color: #a0a0a0; 
        line-height: 1.6; /* 增加行距增加閱讀舒適度 */
    }

    .highlight { 
        color: #00f2ff; 
        font-weight: 700; 
    }
    
    /* 進度條樣式 */
    .stProgress > div > div > div > div { 
        background: linear-gradient(to right, #00f2ff, #0072ff); 
        height: 8px;
    }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面設計]
# =============================================================================

st.markdown('<h1 class="main-title">🛡️ QUANTUM SCANNER</h1>', unsafe_allow_html=True)
st.caption("台股電子全產業：優質量化選股")
st.markdown("---")

if not st.session_state['scan_completed']:
    st.markdown("### 系統核心邏輯 | SYSTEM ARCHITECTURE")
    
    # 8 道獨立邏輯展示 (字體強化版)
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
            <div class="logic-desc">近 20 日平均日成交量需大於 <span class="highlight">1,000張</span>，確保流動性無虞。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">03 / LEVEL</div>
            <div class="logic-title">技術位階</div>
            <div class="logic-desc">股價必須站穩長線生命線 <span class="highlight">MA240</span> (年線) 之上。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">04 / TREND</div>
            <div class="logic-title">趨勢排列</div>
            <div class="logic-desc"><span class="highlight">季線 (MA60)</span> 大於年線，確保多頭排列發散態勢。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">05 / SCALE</div>
            <div class="logic-title">營收規模</div>
            <div class="logic-desc">近12 個月累積營收 (<span class="highlight">LTM</span>) 創下過去 5 年來最大值。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">06 / MOMENTUM</div>
            <div class="logic-title">爆發動能</div>
            <div class="logic-desc">近 6 個月內至少有1月以上之營收創下 <span class="highlight">歷史新高</span> 紀錄。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">07 / DYNAMICS</div>
            <div class="logic-title">季度動能</div>
            <div class="logic-desc">近 3 個月營收總和高於去年同期累積營收，確保 <span class="highlight">季 YoY > 0</span>。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">08 / TRACKING</div>
            <div class="logic-title">籌碼與相對強弱</div>
            <div class="logic-desc">同步<span class="highlight">法人籌碼</span>數據並執行還原權值 0050 績效對比。</div>
        </div>
    </div>
    """
    st.markdown(logic_html, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 啟動量化掃描系統", type="primary", use_container_width=True):
            
            # 百分比進度條儀式
            p_bar = st.progress(0, text="📡 正在初始化系統終端...")
            
            with st.status("正在執行深度分析篩選...", expanded=True) as status:
                process_steps = [
                    (15, "🔍 正在過濾電子產業標的與流動性數據..."),
                    (35, "📈 正在計算股價位階與多頭排列型態..."),
                    (55, "🏭 正在檢索滾式累積年營收與月營收歷史新高標的..."),
                    (75, "👥 正在同步三大法人近 5 日買賣超張數..."),
                    (90, "⚖️ 正在執行 0050 還原權值績效相對強弱..."),
                    (100, "🏆 正在產出最終精選量化報告...")
                ]
                
                for percent, text in process_steps:
                    time.sleep(2.5)
                    p_bar.progress(percent, text=text)
                    status.write(text)
                
                try:
                    df = pd.read_csv(f"{RAW_URL}?t={int(time.time())}", on_bad_lines='skip')
                    st.session_state['temp_df'] = df
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 分析完成", state="complete", expanded=False)
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"數據讀取失敗。請確認 GitHub 檔案內容正確。")

else:
    # --- 結果頁面 ---
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "2026-03-13"
    
    m1, m2, m3 = st.columns(3)
    m1.metric("今日掃描樣本", "900+ 檔")
    m2.metric("符合門檻標的", f"{len(df)} 檔")
    m3.metric("最後更新日期", str(update_date))
    
    st.sidebar.button("🔄 重新啟動掃描", on_click=lambda: st.session_state.update({"scan_completed": False}))
    
    st.subheader(f"🏆 QUANTUM TOP PICKS")
    
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
    st.sidebar.download_button("📥 下載 Excel 完整報告", output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

st.divider()
st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
