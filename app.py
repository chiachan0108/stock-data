import streamlit as st
import pandas as pd
import datetime, io, time

# =============================================================================
# [配置區]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 頁面配置與 時尚科技感 CSS]
# =============================================================================
st.set_page_config(page_title="台股電子量化智選系統", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700&family=JetBrains+Mono:wght@500;700&display=swap');
    
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    
    /* 科技感卡片 */
    .logic-card { 
        background: rgba(255, 255, 255, 0.03); 
        border-left: 3px solid #00f2ff; 
        padding: 18px; 
        border-radius: 10px; 
        margin-bottom: 12px;
        transition: 0.3s;
    }
    .logic-card:hover { background: rgba(0, 242, 255, 0.05); }
    .highlight { color: #ffde59; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
    
    /* 下載按鈕美化 */
    .stDownloadButton button { width: 100%; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面設計]
# =============================================================================
st.title("🛡️ QUANTUM TECH SCANNER")
st.caption("台股電子產業：深度量化與還原權值績效監控")
st.markdown("---")

if not st.session_state['scan_completed']:
    _, center_col, _ = st.columns([1, 6, 1])
    with center_col:
        st.write("### 核心篩選邏輯 | 8-STEP FILTERING")
        st.markdown("""
        <div class="logic-card">📍 <b>Step 1-2: 產業與流動性</b><br>鎖定電子全產業標的，且日均成交量需 <span class="highlight">> 1,000張</span>。</div>
        <div class="logic-card">📈 <b>Step 3-4: 技術位階排列</b><br>站穩 <span class="highlight">MA240</span> 長線支撐，且季線高於年線呈多頭排列。</div>
        <div class="logic-card">🏭 <b>Step 5-7: 營收三冠王驗證</b><br>LTM 創 5 年新高、單月營收創歷史新高、且 <span class="highlight">季 YoY > 0</span>。</div>
        <div class="logic-card">👥 <b>Step 8: 籌碼與績效對比</b><br>同步法人籌碼動向，並計算標的相對於 <span class="highlight">0050</span> 之還原權值強弱。</div>
        """, unsafe_allow_html=True)

        if st.button("🚀 啟動全量量化掃描系統", type="primary", use_container_width=True):
            # 設定 15 秒的模擬掃描儀式 (對應 Colab 的 8 大邏輯)
            with st.status("📡 正在連接大數據終端...", expanded=True) as status:
                time.sleep(2.0); status.write("🔍 正在過濾 900+ 檔電子股流動性...")
                time.sleep(2.5); status.write("📈 正在掃描技術面位階 (MA60, MA240)...")
                time.sleep(2.5); status.write("🏭 正在分析 LTM 累積營收與歷史新高紀錄...")
                time.sleep(2.5); status.write("👥 正在同步近 5 日三大法人籌碼分點...")
                time.sleep(2.5); status.write("⚖️ 正在執行 0050 還原權值績效對標...")
                time.sleep(3.0); status.write("🏆 正在編譯最終精選報告...")
                
                try:
                    # 讀取 Colab 傳上來的 CSV
                    df = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 量化任務掃描完成", state="complete", expanded=False)
                    st.balloons()
                    st.rerun()
                except:
                    st.error("數據同步失敗，請檢查 Colab 是否已成功推送 CSV。")

else:
    # 顯示結果頁面
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "2026-03-13"
    
    # 頂部數據儀表板
    m1, m2, m3 = st.columns(3)
    m1.metric("掃描樣本", "900+ 檔")
    m2.metric("符合門檻", f"{len(df)} 檔")
    m3.metric("更新日期", str(update_date))
    
    st.sidebar.button("🔄 重新執行掃描", on_click=lambda: st.session_state.update({"scan_completed": False}))
    
    st.subheader("🏆 QUANTUM TOP PICKS (依相對強弱排序)")
    
    # 修正色階：確保欄位名稱與 Colab 一致
    styled = df.style.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
    if '近5日法人超(張)' in df.columns:
        styled = styled.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')
    if '近一季相對大盤強弱' in df.columns:
        styled = styled.background_gradient(subset=['近一季相對大盤強弱'], cmap='RdYlGn')

    # 數據格式化顯示
    st.dataframe(styled.format({
        "現價": "{:.2f}", 
        "季乖離(%)": "{:.2f}%", 
        "年乖離(%)": "{:.2f}%", 
        "近一季相對大盤強弱": "{:+.2f}%", # 顯示正負號，體現強弱
        "營收YoY(%)": "{:.2f}%", 
        "營收MoM(%)": "{:.2f}%"
    }), use_container_width=True)
    
    # 下載按鈕
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 下載 Excel 報告", output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

st.divider()
st.caption("QUANTUM DATA ENGINE © 2026 | 深度量化，精準決策。")
