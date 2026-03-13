import streamlit as st
import pandas as pd
import datetime
import io

# =============================================================================
# [核心配置：請修改為您的 GitHub 連結]
# =============================================================================
# 格式範例: https://raw.githubusercontent.com/您的帳號/儲存庫名/main/daily_result.csv
RAW_URL = "https://raw.githubusercontent.com/您的帳號/stock-data/main/daily_result.csv"

# =============================================================================
# [1. 網頁版介面設定]
# =============================================================================
st.set_page_config(page_title="台股電子量化雲端佈告欄", layout="wide")

st.title("🚀 台股電子產業量化：Colab 同步版")
st.markdown(f"本網頁顯示由 **Google Colab** 預先運算的結果，**1 秒載入，完全不消耗 API 額度**。")

# 側邊欄設計
st.sidebar.header("📊 數據管理")
if st.sidebar.button("🔄 刷新最新選股結果"):
    try:
        # 1. 直接從 GitHub 抓取 CSV
        df = pd.read_csv(RAW_URL)
        update_date = df['更新日期'].iloc[0]
        
        st.success(f"✅ 數據載入成功！同步 Colab 更新日期：{update_date}")
        
        # 2. 顯示數據表格與美化
        # 我們使用色階來顯示「年乖離」，顏色越綠代表位階越安全
        st.subheader(f"🏆 電子產業精選名單 ({update_date})")
        st.dataframe(
            df.style.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
                    .background_gradient(subset=['季乖離(%)'], cmap='YlGn')
                    .format({"營收YoY(%)": "{:.2f}%", "營收MoM(%)": "{:.2f}%"})
        )
        
        # 3. 提供專業級 Excel 下載
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
        
        st.download_button(
            label="📥 下載完整 Excel 報告",
            data=output.getvalue(),
            file_name=f"台股量化選股_{update_date}.xlsx",
            mime="application/vnd.ms-excel"
        )
        
    except Exception as e:
        st.error("❌ 無法取得數據。請確認您是否已在 Colab 執行過程式，且 GitHub 網址正確。")
        st.info(f"💡 提示：請檢查 GitHub 是否已有 daily_result.csv 檔案。")
else:
    st.info("💡 點擊左側『刷新』按鈕，即可秒速同步今日 Colab 運算結果。")

# 頁尾說明
st.divider()
st.caption("策略邏輯：現價 > MA240 且 MA60 > MA240 | LTM 營收創 5 年新高 | 6個月內有單月創新高。")
