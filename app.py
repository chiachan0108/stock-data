import streamlit as st
import pandas as pd
import datetime
import io

# =============================================================================
# [核心配置：GitHub 數據來源]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 網頁版頁面配置]
# =============================================================================
st.set_page_config(page_title="台股量化智選系統", layout="wide")

st.title("🚀 台股電子量化：法人籌碼監控版")
st.markdown("本系統秒速載入由 **Google Colab** 結案的數據，並自動標註法人近 5 日買賣超動向。")

# 側邊欄設計
st.sidebar.header("📊 數據管理")
refresh_btn = st.sidebar.button("🔄 刷新獲取最新名單")

# =============================================================================
# [2. 數據讀取與顯示邏輯]
# =============================================================================

# 如果點擊刷新，或者一進網頁自動載入
if refresh_btn or 'is_first_run' not in st.session_state:
    st.session_state['is_first_run'] = False
    try:
        # 讀取數據 (加上 timestamp 避免瀏覽器抓到舊的快取)
        df = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
        
        if df.empty:
            st.warning("⚠️ 讀取成功，但目前沒有符合篩選條件的股票。")
        else:
            update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "未知"
            st.success(f"✅ 數據同步成功！Colab 最後結案日期：{update_date}")
            
            st.subheader(f"🏆 電子產業精選名單 ({update_date})")

            # --- 表格美化邏輯 ---
            # 1. 取得現有的欄位列表，避免寫死欄位名導致報錯
            cols = df.columns.tolist()
            
            # 2. 定義色階樣式
            styled_df = df.style
            
            # [年乖離]：越小(位階低)越綠，越大越紅
            if '年乖離(%)' in cols:
                styled_df = styled_df.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
            
            # [法人超(張)]：買超越多越綠，賣超顯示紅色/淡色
            if '近5日法人超(張)' in cols:
                styled_df = styled_df.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')

            # 3. 顯示表格
            st.dataframe(styled_df.format({
                "現價": "{:.2f}",
                "季乖離(%)": "{:.2f}%",
                "年乖離(%)": "{:.2f}%",
                "營收YoY(%)": "{:.2f}%",
                "營收MoM(%)": "{:.2f}%"
            }), use_container_width=True)
            
            # --- Excel 下載按鈕 ---
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='精選名單')
                workbook  = writer.book
                worksheet = writer.sheets['精選名單']
                header_fmt = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1F4E78', 'border': 1})
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)
                    worksheet.set_column(col_num, col_num, 15)
            
            st.sidebar.download_button(
                label="📥 下載完整 Excel 報告",
                data=output.getvalue(),
                file_name=f"台股選股報告_{update_date}.xlsx",
                mime="application/vnd.ms-excel"
            )

    except Exception as e:
        st.error(f"❌ 無法讀取 GitHub 數據。")
        st.info(f"偵錯訊息：{e}")
else:
    st.info("💡 點擊左側『刷新』按鈕，載入今日最新選股名單。")

st.divider()
st.caption("策略邏輯：長線多頭排列 + LTM 營收五年新高 + 近 5 日法人籌碼監控。")
