import streamlit as st
import pandas as pd
import datetime, io

# [配置]
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

st.set_page_config(page_title="台股量化旗艦版", layout="wide")
st.title("🚀 台股電子量化：法人籌碼監控版")

if st.sidebar.button("🔄 刷新獲取最新數據"):
    try:
        df = pd.read_csv(f"{RAW_URL}?nocache={datetime.datetime.now().timestamp()}")
        update_date = df['更新日期'].iloc[0] if '更新日期' in df.columns else "未知"
        st.success(f"✅ 同步成功！最後更新：{update_date}")

        # 表格美化：對法人買超進行著色
        st.subheader("🏆 電子產業精選名單 (含法人籌碼)")
        
        # 定義樣式
        styled_df = df.style.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
        
        # 如果有法人欄位，對其進行色階處理
        if '近5日法人超(張)' in df.columns:
            styled_df = styled_df.background_gradient(subset=['近5日法人超(張)'], cmap='Greens')

        st.dataframe(styled_df, use_container_width=True)

        # Excel 下載
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='精選名單')
        st.sidebar.download_button("📥 下載 Excel 報告", data=output.getvalue(), file_name=f"量化報告_{update_date}.xlsx")

    except Exception as e:
        st.error(f"❌ 無法讀取數據。錯誤訊息: {e}")
