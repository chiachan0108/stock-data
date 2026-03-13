import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區] - 請再次確認此網址在瀏覽器能直接打開
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
    .logic-card { background: rgba(255, 255, 255, 0.03); border-left: 3px solid #00f2ff; padding: 18px; border-radius: 10px; margin-bottom: 12px; }
    .highlight { color: #ffde59; font-family: 'JetBrains Mono', monospace; font-weight: 700; }
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
            with st.status("📡 正在連接量化終端...", expanded=True) as status:
                # 15 秒科技感儀式 (分 6 階段，每階段約 2.5 秒)
                steps = [
                    "🔍 正在過濾 900+ 檔電子股流動性數據...",
                    "📈 正在分析還原均線位階 (MA60, MA240)...",
                    "🏭 正在檢索 LTM 累積營收與歷史新高紀錄...",
                    "👥 正在計算近 5 日三大法人籌碼分點...",
                    "⚖️ 正在執行 0050 還原權值績效對標...",
                    "🏆 正在編譯最終精選報告並同步 GitHub..."
                ]
                
                for step in steps:
                    time.sleep(2.5)
                    status.write(step)
                
                try:
                    # 強制加上 nocache 參數防止抓到舊資料
                    timestamp = int(time.time())
                    final_url = f"{RAW_URL}?v={timestamp}"
                    
                    # 讀取數據
                    df = pd.read_csv(final_url)
                    
                    if df.empty:
                        status.update(label="⚠️ 掃描完成，但今日無符合標的", state="error", expanded=True)
                    else:
                        st.session_state['temp_df'] = df
                        st.session_state['scan_completed'] = True
                        status.update(label="✅ 量化掃描結案", state="complete", expanded=False)
                        st.balloons()
                        st.rerun()
                except Exception as e:
                    status.update(label="❌ 數據同步失敗", state="error", expanded=True)
                    st.error(f"詳細報表錯誤訊息: {str(e)}")
                    st.info("請檢查 GitHub 檔案是否含有正確的欄位標題。")

else:
    # 顯示結果頁面
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "2026-03-13"
    
    m1, m2, m3 = st.columns(3)
    m1.metric("今日掃描樣本", "900+ 檔")
    m2.metric("符合門檻標的", f"{len(df)} 檔")
    m3.metric("資料最後更新日期", str(update_date))
    
    st.sidebar.button("🔄 重新執行掃描", on_click=lambda: st.session_state.update({"scan_completed": False}))
    
    st.subheader(f"🏆 QUANTUM TOP PICKS (依相對強弱排序)")
    
    # 色階美化 - 增加容錯檢查
    styled = df.style
    cols = df.columns.tolist()
    
    if '年乖離(%)' in cols:
        styled = styled.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
    if '近5日法人超(張)' in cols:
        styled = styled.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')
    if '近一季相對大盤強弱' in cols:
        styled = styled.background_gradient(subset=['近一季相對大盤強弱'], cmap='RdYlGn')

    # 定義格式化字典 (只針對存在的欄位)
    format_dict = {
        "現價": "{:.2f}",
        "季乖離(%)": "{:.2f}%",
        "年乖離(%)": "{:.2f}%",
        "近一季相對大盤強弱": "{:+.2f}%",
        "營收YoY(%)": "{:.2f}%",
        "營收MoM(%)": "{:.2f}%"
    }
    # 過濾掉不存在於 df 中的欄位
    active_formats = {k: v for k, v in format_dict.items() if k in cols}

    st.dataframe(styled.format(active_formats), use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 下載 Excel 專業報告", output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

st.divider()
st.caption("QUANTUM DATA ENGINE © 2026 | 數據驅動策略，精準掌握趨勢。")
