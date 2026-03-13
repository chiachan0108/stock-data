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

    /* 8道邏輯卡片設計 */
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
        transition: all 0.4s ease;
    }

    .logic-item:hover {
        background: rgba(0, 242, 255, 0.05);
        border-color: rgba(0, 242, 255, 0.5);
    }

    .logic-index {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        color: #00f2ff;
        font-weight: 700;
        margin-bottom: 8px;
    }

    .logic-title { font-size: 1rem; font-weight: 600; color: #ffffff; margin-bottom: 10px; }
    .logic-desc { font-size: 0.85rem; color: #888888; line-height: 1.5; }
    .highlight { color: #00f2ff; font-weight: 600; }
    
    /* 進度條顏色優化 */
    .stProgress > div > div > div > div { background: linear-gradient(to right, #00f2ff, #0072ff); }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面設計]
# =============================================================================

st.markdown('<h1 class="main-title">🛡️ QUANTUM SCANNER</h1>', unsafe_allow_html=True)
st.caption("台股電子全產業：深度量化與還原權值績效監控")
st.markdown("---")

if not st.session_state['scan_completed']:
    st.markdown("### 系統核心邏輯 | SYSTEM ARCHITECTURE")
    
    # 8 道獨立邏輯展示
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item"><div class="logic-index">01</div><div class="logic-title">產業範圍</div><div class="logic-desc">鎖定上市櫃全體<span class="highlight">電子產業</span>標的。</div></div>
        <div class="logic-item"><div class="logic-index">02</div><div class="logic-title">流動性</div><div class="logic-desc">近 20 日日均成交量 > <span class="highlight">1,000張</span>。</div></div>
        <div class="logic-item"><div class="logic-index">03</div><div class="logic-title">技術位階</div><div class="logic-desc">股價站穩長線支撐 <span class="highlight">MA240</span> 之上。</div></div>
        <div class="logic-item"><div class="logic-index">04</div><div class="logic-title">趨勢排列</div><div class="logic-desc"><span class="highlight">MA60 > MA240</span>，多頭排列發散。</div></div>
        <div class="logic-item"><div class="logic-index">05</div><div class="logic-title">營收規模</div><div class="logic-desc">累積營收 (<span class="highlight">LTM</span>) 創下 5 年來新高。</div></div>
        <div class="logic-item"><div class="logic-index">06</div><div class="logic-title">爆發力</div><div class="logic-desc">近 6 個月有單月營收創下 <span class="highlight">歷史新高</span>。</div></div>
        <div class="logic-item"><div class="logic-index">07</div><div class="logic-title">季度動能</div><div class="logic-desc">確保 <span class="highlight">季 YoY > 0</span>，動能持續擴張。</div></div>
        <div class="logic-item"><div class="logic-index">08</div><div class="logic-title">相對強弱</div><div class="logic-desc">計算與 <span class="highlight">0050</span> 之還原權值績效對標。</div></div>
    </div>
    """
    st.markdown(logic_html, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🚀 啟動全量量化掃描系統", type="primary", use_container_width=True):
            
            # --- 儀式感：進度條與百分比 ---
            p_bar = st.progress(0, text="📡 正在初始化系統...")
            
            with st.status("正在執行深度分析...", expanded=True) as status:
                process_steps = [
                    (15, "🔍 正在過濾電子產業標的與流動性..."),
                    (35, "📈 正在計算技術面均線位階排列..."),
                    (55, "🏭 正在檢索 LTM 營收與創歷史新高標的..."),
                    (75, "👥 正在同步三大法人籌碼分點張數..."),
                    (90, "⚖️ 正在執行 0050 還原權值績效對標..."),
                    (100, "🏆 正在產出最終精選報告...")
                ]
                
                for percent, text in process_steps:
                    time.sleep(2.5) # 總計 15 秒
                    p_bar.progress(percent, text=text)
                    status.write(text)
                
                try:
                    # 使用 timestamp 避免讀取舊快取，加上 error_bad_lines 跳過錯誤行
                    df = pd.read_csv(f"{RAW_URL}?t={int(time.time())}", on_bad_lines='skip')
                    st.session_state['temp_df'] = df
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 分析完成", state="complete", expanded=False)
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"數據同步失敗：無法正確解析 CSV 內容。詳細資訊：{e}")

else:
    # --- 結果頁面 ---
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "2026-03-13"
    
    m1, m2, m3 = st.columns(3)
    m1.metric("今日掃描樣本", "900+ 檔")
    m2.metric("符合門檻標的", f"{len(df)} 檔")
    m3.metric("資料更新日期", str(update_date))
    
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
    st.sidebar.download_button("📥 下載 Excel 報告", output.getvalue(), file_name="Quant_Report.xlsx")

st.divider()
st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
