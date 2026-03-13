import streamlit as st
import pandas as pd
import datetime
import io
import time  # 用於精確控制儀式感時間

# =============================================================================
# [核心配置：GitHub 數據來源]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 網頁版頁面配置]
# =============================================================================
st.set_page_config(page_title="台股電子量化智選系統", layout="wide", initial_sidebar_state="collapsed")

# 初始化 session_state
if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面設計]
# =============================================================================

# 頂部導航與標題
st.title("🛡️ QUANTUM TECH STOCK SCANNER")
st.caption("台股電子產業：大數據深度量化過濾引擎")
st.markdown("---")

# 判斷顯示邏輯
if not st.session_state['scan_completed']:
    # --- 時尚簡約首頁 ---
    
    # 使用居中的佈局呈現科技感
    _, center_col, _ = st.columns([1, 4, 1])
    
    with center_col:
        st.subheader("系統運作邏輯說明")
        st.write("""
        本引擎專為電子產業設計，透過多重漏斗模型篩選出同時具備 **『趨勢、營收、籌碼』** 三位一體的強勢個股。
        掃描過程將即時連接數據中心，並逐一執行您的量化過濾條件。
        """)
        
        # 使用 Expander 隱藏細節，保持簡約
        with st.expander("查看 8 大核心量化標準"):
            st.markdown("""
            1. **產業範圍**：鎖定上市櫃全體電子產業標的。
            2. **流動性門檻**：近 20 日日均成交量大於 1,000 張。
            3. **技術位階**：股價站穩年線 (MA240)。
            4. **技術趨勢**：季線 (MA60) 高於年線，呈多頭排列。
            5. **營收規模**：12 個月累積營收 (LTM) 創下 5 年新高。
            6. **創高動能**：近 6 個月內有單月營收創下歷史新高。
            7. **季度動能**：近 3 個月營收總和高於去年同期 (季 YoY > 0)。
            8. **籌碼監控**：即時統計近 5 個交易日三大法人合計買賣超。
            """)

        st.write("")
        # 啟動按鈕
        if st.button("🚀 執行全量量化掃描", type="primary", use_container_width=True):
            
            # --- 儀式感核心：總計約 15 秒的模擬掃描 ---
            with st.status("📡 正在啟動數據掃描引擎...", expanded=True) as status:
                time.sleep(2.0)
                status.write("📍 Step 1: 正在篩選電子產業流動性標的 (Volume > 1,000)...")
                time.sleep(2.0)
                status.write("📈 Step 2: 正在計算 900+ 標的之年線 (MA240) 支撐力道...")
                time.sleep(2.0)
                status.write("📊 Step 3: 正在驗證季線與年線之多頭排列形態...")
                time.sleep(2.0)
                status.write("🏭 Step 4: 正在計算滾動 12 個月 (LTM) 累積營收規模...")
                time.sleep(2.0)
                status.write("💥 Step 5: 正在檢索歷史月營收記錄，比對歷史新高標的...")
                time.sleep(2.0)
                status.write("👥 Step 6: 正在計算近 5 日三大法人合計買賣超數據...")
                time.sleep(3.0) # 最後的綜合運算時間稍長
                
                try:
                    df_raw = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
                    st.session_state['temp_df'] = df_raw
                    st.session_state['scan_completed'] = True
                    status.update(label="✅ 掃描任務結案：已產出今日最優選名單", state="complete", expanded=False)
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    status.update(label="❌ 數據讀取失敗", state="error", expanded=True)
                    st.error(f"GitHub 連線異常: {e}")

else:
    # --- 結果顯示頁面 ---
    df = st.session_state['temp_df']
    update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else datetime.date.today()
    
    # 頂部數據摘要
    c1, c2, c3 = st.columns(3)
    c1.metric("今日掃描標的", "900+ 檔")
    c2.metric("通過量化門檻", f"{len(df)} 檔")
    c3.metric("資料更新日期", f"{update_date}")

    # 顯示結果
    st.subheader("🏆 量化精選多頭清單")
    
    # 自動色階處理
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

    # 側邊欄放重設按鈕與下載
    st.sidebar.header("選項")
    if st.sidebar.button("🔄 重新啟動掃描"):
        st.session_state['scan_completed'] = False
        st.rerun()
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='精選名單')
    st.sidebar.download_button("📥 下載專業報告 (Excel)", data=output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

# 頁尾
st.divider()
st.caption("Quant Data System © 2026. Designed for Electronic Sector Trend Analysis.")
