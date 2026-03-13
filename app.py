import streamlit as st
import pandas as pd
import datetime
import io

# =============================================================================
# [核心配置：GitHub 數據來源]
# =============================================================================
# 已根據您的需求更新為指定的原始連結
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 網頁版頁面配置]
# =============================================================================
st.set_page_config(page_title="台股電子量化雲端版", layout="wide")

st.title("🚀 台股電子產業量化：Colab 預運算展示版")
st.markdown("本系統秒速讀取由 **Google Colab** 結案的數據，不再重複執行運算，省時且節省 API 額度。")

# 側邊欄設計
st.sidebar.header("📊 數據控制面板")
refresh_btn = st.sidebar.button("🔄 刷新最新掃描結果")

# =============================================================================
# [2. 數據讀取與顯示邏輯]
# =============================================================================

# 如果點擊刷新，或者一進網頁自動載入（這裡設定預設顯示）
if refresh_btn or 'is_first_run' not in st.session_state:
    st.session_state['is_first_run'] = False
    try:
        # 1. 直接讀取 GitHub 上的 CSV 數據
        # 加上 random 參數避免瀏覽器快取舊資料
        df = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
        
        if df.empty:
            st.warning("⚠️ 讀取到檔案，但目前內容為空。請確認 Colab 是否有成功篩選出標的。")
        else:
            # 2. 顯示更新資訊
            # 優先嘗試取得更新日期欄位
            update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else datetime.date.today().strftime('%Y-%m-%d')
            st.success(f"✅ 數據載入成功！Colab 最後同步日期：{update_date}")
            
            # 3. 欄位自動相容處理 (避免因為欄位名稱微差導致樣式崩潰)
            # 找出包含「乖離」字眼的欄位作為熱點圖對象
            bias_cols = [c for c in df.columns if '乖離' in c]
            yoy_col = next((c for c in df.columns if 'YoY' in c), None)
            mom_col = next((c for c in df.columns if 'MoM' in c), None)

            # 4. 顯示美化表格
            st.subheader(f"🏆 電子產業精選名單 ({update_date})")
            
            # 設定樣式：年乖離使用色階（綠色代表低位階），YoY/MoM 正數顯示紅色
            styled_df = df.style
            if bias_cols:
                # 年乖離越小（靠近年線）顯示綠色，越大顯示紅色
                styled_df = styled_df.background_gradient(subset=[bias_cols[-1]], cmap='RdYlGn_r')
            
            # 格式化百分比顯示
            format_dict = {}
            if yoy_col: format_dict[yoy_col] = "{:.2f}%"
            if mom_col: format_dict[mom_col] = "{:.2f}%"
            
            st.dataframe(styled_df.format(format_dict), use_container_width=True)
            
            # 5. 提供專業級 Excel 報告下載
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='精選名單')
                
                # 進階 Excel 美編
                workbook  = writer.book
                worksheet = writer.sheets['精選名單']
                header_fmt = workbook.add_format({'bold': True, 'font_color': 'white', 'bg_color': '#1F4E78', 'border': 1})
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)
                    worksheet.set_column(col_num, col_num, 15)
            
            st.sidebar.download_button(
                label="📥 下載 Excel 報告",
                data=output.getvalue(),
                file_name=f"台股選股報告_{update_date}.xlsx",
                mime="application/vnd.ms-excel"
            )

    except Exception as e:
        st.error("❌ 無法獲取 GitHub 數據。")
        st.info(f"偵錯資訊：{str(e)}")
        st.markdown(f"請確認此連結是否可正常開啟：[點我檢查原始數據]({RAW_URL})")

else:
    st.info("💡 點擊左側按鈕即可秒速同步今日 Colab 運算結果。")

# 頁尾說明區
st.divider()
st.caption("🔍 篩選邏輯：現價 > MA240、季線 > 年線 (趨勢多頭) | LTM 營收創 5 年新高 | 近 6 個月有單月創歷史新高 | 季 YoY 正成長。")
