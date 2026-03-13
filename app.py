import streamlit as st
import pandas as pd
import datetime
import io
import time  # 用於模擬讀取時間，增加儀式感

# =============================================================================
# [核心配置：GitHub 數據來源]
# =============================================================================
# 請確認此連結的中間是您的 GitHub 帳號，且儲存庫與檔名皆正確
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 網頁版頁面配置]
# =============================================================================
st.set_page_config(page_title="台股電子量化智選系統", layout="wide", initial_sidebar_state="collapsed")

# 初始化 session_state，用於控制畫面顯示
if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False
if 'temp_df' not in st.session_state:
    st.session_state['temp_df'] = None

# =============================================================================
# [2. 主介面設計]
# =============================================================================

# 設定具科技感的標題與頁首
st.title("🛡️ 台股電子產業：量化趨勢掃描儀")
st.markdown("---")

# 判斷目前應該顯示首頁還是結果頁
if not st.session_state['scan_completed']:
    # --- 1. 專業科技感首頁 ---
    
    # 建立兩欄式佈局，左邊放文字與按鈕，右邊放科技圖
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("歡迎使用 AI 量化選股系統")
        st.write("""
        本系統整合了 **FinMind API** 與 **Yahoo Finance** 的大數據運算，
        專注於篩選電子產業中具備以下特質的標的：
        
        - 📈 **趨勢強勁**：股價站穩年線 (MA240)，且季線 (MA60) 與年線呈多頭排列。
        - 💰 **營運動能**：累積營收創 5 年新高，且具備單月營收創歷史新高的爆發力。
        - 🏢 **法人認養**：即時追蹤近 5 個交易日三大法人籌碼合計買賣超動向。
        """)
        
        st.info("💡 提示：本系統將秒速讀取已在 Colab 完成結案的數據，不再重複消耗您的 API 額度。")
        
        # 儀式感核心：大型醒目的啟動按鈕
        st.markdown("###") # 增加一些垂直間距
        if st.button("🚀 啟動全量量化掃描", type="primary", use_container_width=True):
            
            # --- 儀式感核心：模擬 10 秒的大數據掃描進度 ---
            with st.status("📡 正在與 FinMind 伺服器建立加密連線...", expanded=True) as status:
                time.sleep(1.0)
                status.write("📊 正在下載台股電子全產業技術面數據 (900+ 標的)...")
                time.sleep(2.0)
                status.write("🧬 正在執行漏斗篩選：現價 > MA240、MA60 > MA240...")
                time.sleep(2.0)
                status.write("🏭 正在計算 LTM 營收動能與創歷史新高邏輯...")
                time.sleep(1.5)
                status.write("👥 正在同步近 5 日三大法人合計買賣超張數...")
                time.sleep(1.5)
                status.write("🏆 正在彙整綜合評分與產出最終精選名單...")
                time.sleep(1.0)
                
                # 實際抓取數據
                try:
                    # 加上 timestamp 避免瀏覽器抓到舊資料
                    df_raw = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df_raw
                    st.session_state['scan_completed'] = True
                    
                    # 更新狀態並重新整理畫面
                    status.update(label="✅ 量化掃描任務完成！", state="complete", expanded=False)
                    st.balloons() # 噴出氣球增加儀式感與慶祝感
                    st.rerun() # 重新整理以顯示數據表格
                    
                except Exception as e:
                    status.update(label="❌ 連線失敗", state="error", expanded=True)
                    st.error(f"無法讀取數據。錯誤訊息: {e}")
                    st.info(f"請確認 Colab 是否已成功推送 `daily_result.csv` 至 GitHub，且連結 `{RAW_URL}` 是正確的。")

    with col2:
        # 在右側放置一張專業、具科技感的插圖
        st.image("https://img.freepik.com/free-vector/digital-global-stock-market-financial-chart-concept-abstract-background_1017-31652.jpg", caption="Quant Data Analysis Engine", use_column_width=True)

else:
    # --- 2. 專業結果顯示頁面 ---
    
    df = st.session_state['temp_df']
    
    # 從 CSV 中取得 Colab 的更新日期
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else datetime.date.today().strftime('%Y-%m-%d')
    
    # 側邊欄控制
    st.sidebar.header("⚙️ 篩選控制")
    if st.sidebar.button("🔄 重新掃描"):
        st.session_state['scan_completed'] = False
        st.rerun()
        
    # 顯示成功總結區
    st.success(f"🎊 掃描完畢！今日共有 **{len(df)}** 檔標的符合量化趨勢篩選門檻。 (更新日期：{update_date})")
    
    # 數據表格顯示與視覺化美化
    st.subheader(f"🏆 台股電子產業：精選多頭清單 ({update_date})")
    
    # 自動找出需要設定色階的欄位，防止因為欄位微差導致崩潰
    bias_cols = [c for c in df.columns if '乖離' in c]
    inst_col = [c for c in df.columns if '法人超' in c]
    
    # 設定表格樣式：年乖離色階（紅漲綠跌）、法人色階（綠色買超）
    styled_df = df.style
    if bias_cols:
        styled_df = styled_df.background_gradient(subset=[bias_cols[-1]], cmap='RdYlGn_r')
    if inst_col:
        styled_df = styled_df.background_gradient(subset=[inst_col[-1]], cmap='Greens')

    # 顯示表格並設定百分比格式
    st.dataframe(styled_df.format({
        "現價": "{:.2f}",
        "季乖離(%)": "{:.2f}%",
        "年乖離(%)": "{:.2f}%",
        "營收YoY(%)": "{:.2f}%",
        "營收MoM(%)": "{:.2f}%"
    }), use_container_width=True)

    # 專業 Excel 報告下載按鈕
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='精選名單')
        
        # 獲取 xlsxwriter 物件進行進階美化
        workbook  = writer.book
        worksheet = writer.sheets['精選名單']
        header_fmt = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1F4E78'})
        
        for col_num, value in enumerate(df.columns.values):
            worksheet.write(0, col_num, value, header_fmt)
            worksheet.set_column(col_num, col_num, 15)
            
    st.sidebar.download_button(
        label="📥 下載完整 Excel 報告",
        data=output.getvalue(),
        file_name=f"台股選股報告_{update_date}.xlsx",
        mime="application/vnd.ms-excel"
    )

# 頁尾
st.divider()
st.caption("聲明：本數據僅供量化研究與策略教學參考，不構成任何投資建議。投資人應獨立判斷並自負風險。")
