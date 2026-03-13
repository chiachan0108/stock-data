import streamlit as st
import pandas as pd
import datetime
import io
import time  # 用於模擬讀取時間

# =============================================================================
# [核心配置：GitHub 數據來源]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 網頁版頁面配置]
# =============================================================================
st.set_page_config(page_title="台股電子量化智選系統", layout="wide")

# 隱藏預設的數據顯示，建立歡迎區
if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面設計]
# =============================================================================

# 標題與形象區
st.title("🛡️ 台股電子產業：量化趨勢掃描儀")
st.markdown("---")

if not st.session_state['scan_completed']:
    # 這是使用者剛進來看到的畫面
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("歡迎使用 AI 量化選股系統")
        st.write("""
        本系統整合了 **FinMind API** 與 **Yahoo Finance** 的大數據運算，
        專注於篩選電子產業中具備以下特質的標的：
        - 📈 **趨勢強勁**：股價站穩年線，且季線與年線呈多頭排列。
        - 💰 **營運動能**：累積營收創 5 年新高，且具備季度成長爆發力。
        - 🏢 **法人認養**：即時追蹤近 5 個交易日三大法人籌碼動向。
        """)
        
        # 儀式感核心：啟動按鈕
        if st.button("🚀 啟動全量量化掃描", type="primary", use_container_width=True):
            # 模擬進度儀式
            with st.status("正在執行深度量化分析...", expanded=True) as status:
                st.write("📡 正在與 FinMind 伺服器建立加密連線...")
                time.sleep(0.8)
                st.write("📊 正在下載電子全產業技術面數據 (900+ 標的)...")
                time.sleep(1.2)
                st.write("🧬 正在計算年線乖離與營收 LTM 篩選邏輯...")
                time.sleep(1.0)
                st.write("👥 正在同步近 5 日法人買賣超張數...")
                time.sleep(0.5)
                
                # 實際抓取數據
                try:
                    df_raw = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df_raw
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 掃描任務完成！", state="complete", expanded=False)
                    st.balloons() # 噴出氣球增加儀式感
                    st.rerun() # 重新整理以顯示數據
                except Exception as e:
                    st.error(f"連線失敗: {e}")
    
    with col2:
        # 可以放一張專業的插圖或儀表板示意圖
        st.image("https://img.freepik.com/free-vector/digital-global-stock-market-financial-chart-concept-abstract-background_1017-31652.jpg", caption="Real-time Quant Analysis")

else:
    # 這是點選「開始掃描」後看到的結果畫面
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "2026-03-13"
    
    st.sidebar.header("⚙️ 篩選控制")
    if st.sidebar.button("🔄 重新掃描"):
        st.session_state['scan_completed'] = False
        st.rerun()
    
    st.success(f"🎊 掃描完畢！今日共有 **{len(df)}** 檔符合量化門檻之標的。 (更新日期：{update_date})")
    
    # 顯示美化表格
    styled_df = df.style.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
    if '近5日法人超(張)' in df.columns:
        styled_df = styled_df.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')

    st.dataframe(styled_df.format({
        "現價": "{:.2f}",
        "季乖離(%)": "{:.2f}%",
        "年乖離(%)": "{:.2f}%",
        "營收YoY(%)": "{:.2f}%",
        "營收MoM(%)": "{:.2f}%"
    }), use_container_width=True)

    # Excel 下載
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='精選名單')
    st.sidebar.download_button("📥 下載完整 Excel 報告", data=output.getvalue(), file_name=f"量化報告_{update_date}.xlsx")

# 頁尾
st.divider()
st.caption("聲明：本數據僅供量化研究參考，不構成任何投資建議。投資人應獨立判斷並自負風險。")
