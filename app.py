import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區]
# =============================================================================
GITHUB_USER = "chiachan0108"
GITHUB_REPO = "stock-data"

st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

# 💡 視覺系統 18.0：轉折訊號發光增強版
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&family=Noto+Sans+TC:wght@100;300;400;500;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', 'Noto Sans TC', sans-serif !important; 
        background-color: #0b0f19 !important; color: #e2e8f0 !important;
    }

    .header-group { margin-top: -45px; margin-bottom: 10px; }
    .main-title { 
        font-family: 'JetBrains Mono', monospace !important; font-weight: 700; letter-spacing: -2px; 
        background: linear-gradient(90deg, #00f2ff, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        font-size: clamp(2.2rem, 6vw, 3.8rem); line-height: 1.1; margin: 0;
    }
    
    .status-pill {
        display: inline-flex; align-items: center; background: rgba(0, 242, 255, 0.05);
        border: 1px solid rgba(0, 242, 255, 0.2); padding: 6px 16px; border-radius: 50px;
        font-size: 0.75rem; color: #00f2ff; margin-bottom: 15px;
    }
    .pulse-dot {
        height: 8px; width: 8px; background-color: #00f2ff; border-radius: 50%;
        display: inline-block; margin-right: 10px; box-shadow: 0 0 8px #00f2ff;
        animation: pulse 2s infinite;
    }
    @keyframes pulse { 0% { opacity: 0.5; } 50% { opacity: 1; } 100% { opacity: 0.5; } }

    .section-label {
        font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: #00f2ff;
        letter-spacing: 2px; margin-top: 20px; margin-bottom: 12px; font-weight: 600; text-transform: uppercase;
        display: flex; align-items: center; white-space: nowrap;
    }
    .section-label::after {
        content: ""; flex: 1; height: 1px; background: linear-gradient(90deg, rgba(0, 242, 255, 0.3), transparent); margin-left: 15px;
    }

    [data-testid="stDataFrame"] {
        background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 16px;
        border: 1px solid rgba(0, 242, 255, 0.15); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }

    .disclaimer-box {
        background: rgba(30, 41, 59, 0.3); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #00f2ff; 
        padding: 24px; border-radius: 12px; margin: 40px 0; display: flex; align-items: flex-start; gap: 16px;
    }
    </style>
""", unsafe_allow_html=True)

# 💡 著色函數：策略 A 專用紅綠
def color_tw(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    if val > 0: return 'color: #ff4d4f; font-weight: 600;'
    elif val < 0: return 'color: #00e676; font-weight: 600;'
    return 'color: #94a3b8;'

# 💡 著色函數：策略 B & C 專用量子藍
def color_tech_blue(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    return 'color: #00f2ff; font-weight: 600;'

# 💡 核心優化：轉折向上高亮邏輯 (行級別渲染)
def highlight_pivot(row):
    style = [''] * len(row)
    # 如果 現價 > 轉折值，則整行給予一個淡淡的電光藍發光背景
    if "轉折值" in row.index and row["現價"] > row["轉折值"]:
        style = ['background-color: rgba(0, 242, 255, 0.08); border-bottom: 1px solid rgba(0, 242, 255, 0.2);'] * len(row)
    return style

if 'scan_completed' not in st.session_state: st.session_state['scan_completed'] = False
now_taipei = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=8)
data_date = now_taipei.strftime('%Y-%m-%d') if now_taipei.hour >= 20 else (now_taipei - datetime.timedelta(days=1)).strftime('%Y-%m-%d')

# 頂部渲染
st.markdown(f'''
    <div class="header-group">
        <h1 class="main-title">QUANTUM SCANNER</h1>
        <div class="sub-title">台股智能量化篩選系統</div>
        <div class="status-pill">
            <span class="pulse-dot"></span>
            每日 20:00 更新資料庫 &nbsp; | &nbsp; 最後更新日：{data_date}
        </div>
    </div>
''', unsafe_allow_html=True)

if not st.session_state['scan_completed']:
    st.markdown("<div class='section-label'>STRATEGY CONFIGURATION 策略選取</div>", unsafe_allow_html=True)
    strategy_options = ["A. 營收動能型 (基本面優先)", "B. 股價動能型 (技術面優先)", "C. 營收、股價動能雙吻合"]
    strategy_choice = st.selectbox("量化策略模組", strategy_options, label_visibility="collapsed")
    
    st.markdown("<div class='section-label'>SYSTEM ARCHITECTURE 系統核心邏輯</div>", unsafe_allow_html=True)
    # (此處保留原有 logic_html 邏輯，代碼略...)
    st.markdown("🔍 正在初始化數據終端並驗證權限...", unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🚀 啟動AI量化篩選", use_container_width=True):
            with st.status("正在執行深度運算...", expanded=True) as status:
                time.sleep(2) # 保持搜尋質感
                try:
                    ts = int(time.time())
                    url_1 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/daily_result.csv?t={ts}"
                    url_2 = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/main/momentum_result.csv?t={ts}"
                    
                    if "A." in strategy_choice:
                        df_f = pd.read_csv(url_1)
                    elif "B." in strategy_choice:
                        df_f = pd.read_csv(url_2)
                    else:
                        df1, df2 = pd.read_csv(url_1), pd.read_csv(url_2)
                        df1['股價代號'], df2['股價代號'] = df1['股價代號'].astype(str), df2['股價代號'].astype(str)
                        chip_col = [c for c in df2.columns if '法人' in c or '買超' in c][0]
                        df_f = pd.merge(df1, df2[['股價代號', '240日報酬(%)', '20日報酬(%)', chip_col]], on='股價代號', how='inner')

                    if not df_f.empty:
                        df_f.index = range(1, len(df_f) + 1)
                        st.session_state['temp_df'] = df_f
                        st.session_state['selected_strategy'] = strategy_choice
                        st.session_state['scan_completed'] = True
                        st.rerun()
                except Exception as e: st.error(f"⚠️ 連線異常：{str(e)}")
else:
    df = st.session_state['temp_df']
    strategy_choice = st.session_state['selected_strategy']
    
    m1, m2, m3 = st.columns(3)
    m1.metric("🎯 符合標的", f"{len(df)} 檔")
    m2.metric("📅 數據基準日", str(data_date))
    m3.metric("🧠 策略模組", strategy_choice.split('.')[0])
    
    st.button("🔄 重新選擇策略", on_click=lambda: st.session_state.update({"scan_completed": False}), use_container_width=True)
    st.markdown(f"### 🏆 TOP PICKS : {strategy_choice}")
    
    # 💡 渲染與標記邏輯
    if "A." in strategy_choice:
        display_cols = ["股價代號", "公司名稱", "產業別", "現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近20日法人買賣超(張數)", "轉折值"]
        color_cols = ["季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營超YoY(%)", "近20日法人買賣超(張數)"]
        format_dict = {c: "{:.2f}" for c in ["現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "轉折值"]}
        format_dict["近20日法人買賣超(張數)"] = "{:,.0f}"
        
        # 💡 先應用行高亮 (現價 > 轉折值)，再應用文字著色
        styled_df = df[display_cols].style.apply(highlight_pivot, axis=1)\
                    .format(format_dict, na_rep="-")\
                    .map(color_tw, subset=color_cols)
    else:
        # 策略 B 或 C
        if "B." in strategy_choice:
            display_cols = ['股價代號', '公司名稱', '產業別', '現價', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)', '轉折值']
            df_display = df[display_cols].rename(columns={'近20日法人買賣超(張)': '近20日法人買超(張)'})
            color_cols = ["240日報酬(%)", "20日報酬(%)", "近20日法人買超(張)", "轉折值"]
        else: # 策略 C
            chip_col = [c for c in df.columns if '法人' in c or '買超' in c][0]
            display_cols = ['股價代號', '公司名稱', '產業別', '現價', '今年以來累積營收YoY(%)', '240日報酬(%)', '20日報酬(%)', chip_col, '轉折值']
            df_display = df[display_cols]
            color_cols = ['今年以來累積營收YoY(%)', '240日報酬(%)', '20日報酬(%)', chip_col, '轉折值']
            
        styled_df = df_display.style.apply(highlight_pivot, axis=1)\
                    .format({c: "{:.2f}" for c in df_display.columns if "名稱" not in c and "代號" not in c and "產業" not in c}, na_rep="-")\
                    .map(color_tech_blue, subset=color_cols)

    st.dataframe(styled_df, use_container_width=True)
    st.markdown('''<div class="disclaimer-box">🛡️ <div class="disclaimer-text"><span class="disclaimer-bold">重要提醒：</span>高亮背景代表「現價 > 轉折值」，技術面上屬於強勢轉折向上區間。</div></div>''', unsafe_allow_html=True)
    st.download_button("📥 下載 Excel 數據報告", df.to_csv(index=False).encode('utf-8-sig'), file_name=f"Quant_Report_{data_date}.csv")

st.divider(); st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
