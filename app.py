import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區]
# =============================================================================
GITHUB_USER = "chiachan0108"
GITHUB_REPO = "stock-data"

st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

# 💡 視覺系統 21.0：透析數據文案更新、結尾 2 秒定格優化
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;700&family=Noto+Sans+TC:wght@100;300;400;500;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', 'Noto Sans TC', sans-serif !important; 
        background-color: #0b0f19 !important; color: #e2e8f0 !important;
    }

    /* 頂部區域 */
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
    @media (max-width: 480px) { .section-label { font-size: 0.7rem !important; letter-spacing: 1px !important; } }

    /* 4 欄邏輯圖塊 */
    .logic-grid { display: grid; gap: 15px; grid-template-columns: repeat(1, 1fr); margin-bottom: 30px; }
    @media (min-width: 1024px) { .logic-grid { grid-template-columns: repeat(4, 1fr) !important; } }
    .logic-item { 
        background: #161b22; border: 1px solid rgba(148, 163, 184, 0.15); 
        border-top: 3px solid #00f2ff; border-radius: 12px; padding: 20px; transition: 0.3s;
    }
    .logic-item:hover { background: #1c2331; transform: translateY(-3px); }
    .logic-header { display: flex; align-items: center; margin-bottom: 12px; gap: 10px; }
    .logic-icon { font-size: 1.2rem; }
    .logic-index { font-family: 'JetBrains Mono', monospace; font-size: 0.75rem; color: #00f2ff; }
    .logic-subtitle { font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .logic-desc { font-size: 0.85rem; color: #94a3b8; line-height: 1.6; }
    .highlight { color: #ffffff; font-weight: 600; background: rgba(0, 242, 255, 0.1); padding: 0 4px; border-bottom: 1px solid #00f2ff; }

    /* 表格與按鈕 */
    [data-testid="stDataFrame"] {
        background: rgba(15, 23, 42, 0.5); padding: 12px; border-radius: 16px;
        border: 1px solid rgba(0, 242, 255, 0.15); box-shadow: 0 8px 30px rgba(0, 0, 0, 0.4);
    }
    .stButton > button {
        background: linear-gradient(90deg, #00f2ff, #0072ff) !important;
        color: white !important; border: none !important; border-radius: 8px !important; 
        font-weight: 700 !important; letter-spacing: 1px; padding: 12px 0 !important; width: 100% !important; min-height: 50px !important;
    }

    /* 磨砂玻璃免責聲明 */
    .disclaimer-box {
        background: rgba(30, 41, 59, 0.3); backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.05); border-left: 4px solid #00f2ff; 
        padding: 24px; border-radius: 12px; margin: 40px 0; display: flex; align-items: flex-start; gap: 16px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .disclaimer-icon { font-size: 1.4rem; filter: drop-shadow(0 0 8px rgba(0, 242, 255, 0.4)); margin-top: -2px; }
    .disclaimer-text { font-size: 0.88rem; color: #94a3b8; line-height: 1.8; letter-spacing: 0.5px; }
    .disclaimer-bold { color: #f8fafc; font-weight: 600; margin-bottom: 4px; display: block; font-size: 0.95rem; }
    </style>
""", unsafe_allow_html=True)

# 💡 著色函數
def color_tw(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    if val > 0: return 'color: #ff4d4f; font-weight: 600;'
    elif val < 0: return 'color: #00e676; font-weight: 600;'
    return 'color: #94a3b8;'

def color_tech_blue(val):
    if pd.isna(val) or not isinstance(val, (int, float)): return ''
    return 'color: #00f2ff; font-weight: 600;'

def highlight_pivot(row):
    style = [''] * len(row)
    if "轉折值" in row.index and row["現價"] > row["轉折值"] and row["轉折值"] > 0:
        style = ['background-color: rgba(0, 242, 255, 0.12); border-bottom: 1px solid rgba(0, 242, 255, 0.3);'] * len(row)
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

    if "A." in strategy_choice:
        TARGET_MODE = "single_1"
        logic_html = """<div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🎯</span><span class="logic-index">01/SCOPE</span></div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">鎖定台灣上市櫃<span class="highlight">普通股</span>標的。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🌊</span><span class="logic-index">02/LIQUIDITY</span></div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均成交量需大於 <span class="highlight">1,000張</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">⚖️</span><span class="logic-index">03/LEVEL</span></div><div class="logic-subtitle">技術位階</div><div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">📈</span><span class="logic-index">04/TREND</span></div><div class="logic-subtitle">趨勢排列</div><div class="logic-desc"><span class="highlight">MA60 > MA240</span>，呈現多頭排列趨勢。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">👑</span><span class="logic-index">05/SCALE</span></div><div class="logic-subtitle">營收規模</div><div class="logic-desc">近 12 個月累積營收 (LTM) 創下 <span class="highlight">5年來最高</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🔥</span><span class="logic-index">06/MOMENTUM</span></div><div class="logic-subtitle">創高動能</div><div class="logic-desc">近 6 個月內至少有單月營收創下 <span class="highlight">歷史新高</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">⚡</span><span class="logic-index">07/DYNAMICS</span></div><div class="logic-subtitle">雙重成長</div><div class="logic-desc">確保近1季 YoY > 0 且 <span class="highlight">今年累計 YoY > 0</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🏦</span><span class="logic-index">08/TRACKING</span></div><div class="logic-subtitle">法人佈局</div><div class="logic-desc">追蹤近 <span class="highlight">20 日三大法人</span> 淨買賣超張數。</div></div>
        </div>"""
    elif "B." in strategy_choice:
        TARGET_MODE = "single_2"
        logic_html = """<div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🎯</span><span class="logic-index">01/SCOPE</span></div><div class="logic-subtitle">選股範圍</div><div class="logic-desc">全體上市櫃，嚴格排除 <span class="highlight">ETF、權證</span> 等非普通股。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🌊</span><span class="logic-index">02/LIQUIDITY</span></div><div class="logic-subtitle">流動性門檻</div><div class="logic-desc">近20日平均成交量需大於 <span class="highlight">1,000張</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">📊</span><span class="logic-index">03/TRACKING</span></div><div class="logic-subtitle">雙週期比對</div><div class="logic-desc">股價 240 日與 20 日績效需 <span class="highlight">超越大盤同期</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🏦</span><span class="logic-index">04/SMART MONEY</span></div><div class="logic-subtitle">法人護航</div><div class="logic-desc">近 20 個交易日三大法人呈現 <span class="highlight">淨買超</span> 狀態。</div></div>
        </div>"""
    else:
        TARGET_MODE = "dual_intersection"
        logic_html = """<div class="logic-grid">
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🧬</span><span class="logic-index">01/INTERSECTION</span></div><div class="logic-subtitle">雙引擎交集</div><div class="logic-desc">自動抓出具備 <span class="highlight">營收創高</span> 與 <span class="highlight">技術強勢</span> 的標的。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">👑</span><span class="logic-index">02/FUNDAMENTAL</span></div><div class="logic-subtitle">基本面護城河</div><div class="logic-desc">營收創 5 年新高，且近1季與 <span class="highlight">今年累計營收</span> 正成長。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">📈</span><span class="logic-index">03/TECHNICAL</span></div><div class="logic-subtitle">技術面爆發</div><div class="logic-desc">均線多頭排列，且績效皆 <span class="highlight">超越大盤同期</span>。</div></div>
            <div class="logic-item"><div class="logic-header"><span class="logic-icon">🏦</span><span class="logic-index">04/SMART MONEY</span></div><div class="logic-subtitle">法人雙重認同</div><div class="logic-desc">確保近 <span class="highlight">20 日三大法人</span> 淨買超且營收正成長。</div></div>
        </div>"""
    
    st.markdown(logic_html, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🚀 啟動AI量化篩選", use_container_width=True):
            
            # 💡 定義不同策略的 15 秒掃描提示詞
            if "A." in strategy_choice:
                status_title = "🧬 AI 營收動能引擎執行深度掃描..."
                steps = [
                    (20, "🔍 掃描全市場普通股長線多頭排列...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>鎖定 MA60 > MA240 技術位階...</span>"),
                    (40, "🏭 深度運算 5 年 LTM 營收成長曲線...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>營收規模創高驗證完成...</span>"),
                    (60, "⚡ 驗證 YoY 雙重成長與財務護城河...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>排除短期營收動能衰退標的...</span>"),
                    (80, "🏦 疊加近 20 日三大法人籌碼狀態...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>籌碼集中度與聰明錢分析完成...</span>"),
                    (100, "🏆 彙整基本面極端強勢名單...", "<span style='color:#00f2ff; font-family:monospace;'>[SYSTEM]</span> <span style='color:#e2e8f0; font-weight:600;'>AI量化運算結束，準備透析最終數據...</span>")
                ]
            elif "B." in strategy_choice:
                status_title = "🚀 AI 股價動能引擎執行深度掃描..."
                steps = [
                    (20, "🌊 過濾全市場流動性與非普通股標的...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>排除 ETF、權證及低流動性標的...</span>"),
                    (40, "📈 展開 240 日與 20 日雙週期報酬計算...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>動能基準線與歷史波動率建立中...</span>"),
                    (60, "⚔️ 對標大盤績效進行 Alpha 值剔除...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>已鎖定具備相對超額報酬之標的...</span>"),
                    (80, "🏦 追蹤聰明錢流向與主力籌碼堆疊...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>法人淨買超狀態確認完成...</span>"),
                    (100, "🏆 彙整技術面極端強勢名單...", "<span style='color:#00f2ff; font-family:monospace;'>[SYSTEM]</span> <span style='color:#e2e8f0; font-weight:600;'>AI量化運算結束，準備透析最終數據...</span>")
                ]
            else:
                status_title = "🌌 量子雙引擎交集模組執行深度掃描..."
                steps = [
                    (20, "🧬 同步載入 [模組 A] 與 [模組 B] 底層數據...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>雙軌運算資料庫建立完成...</span>"),
                    (40, "⚡ 執行營收創高與相對強勢碰撞測試...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>核心條件交集過濾進行中...</span>"),
                    (60, "👑 提取雙重吻合之極端強勢標的...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>勝率模型收斂，剔除單邊弱勢股...</span>"),
                    (80, "🏦 進行最終法人籌碼雙重認證...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>聰明錢長短線佈局過濾完成...</span>"),
                    (100, "🏆 彙整雙引擎最終交集名單...", "<span style='color:#00f2ff; font-family:monospace;'>[SYSTEM]</span> <span style='color:#e2e8f0; font-weight:600;'>AI量化運算結束，準備透析最終數據...</span>")
                ]

            p_bar = st.progress(0, text="📡 正在初始化數據終端...")
            with st.status(status_title, expanded=True) as status:
                for progress_val, bar_text, status_msg in steps:
                    time.sleep(3) # 每個階段 3 秒
                    p_bar.progress(progress_val, text=bar_text)
                    status.markdown(status_msg, unsafe_allow_html=True)
                
                # 💡 儀式感加強：出現最終文字後額外定格等待 2 秒
                time.sleep(2)
                
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
                except Exception as e: st.error(f"⚠️ 連線異常，請確認資料源：{str(e)}")
else:
    df = st.session_state['temp_df']
    strategy_choice = st.session_state['selected_strategy']
    m1, m2, m3 = st.columns(3)
    m1.metric("🎯 符合標的", f"{len(df)} 檔")
    m2.metric("📅 數據基準日", str(data_date))
    m3.metric("🧠 策略模組", strategy_choice.split('.')[0])
    st.button("🔄 重新選擇策略", on_click=lambda: st.session_state.update({"scan_completed": False}), use_container_width=True)
    st.markdown(f"### 🏆 TOP PICKS : {strategy_choice}")
    
    # 渲染 A 策略表格
    if "A." in strategy_choice:
        display_cols = ["股價代號", "公司名稱", "產業別", "現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近20日法人買賣超(張數)"]
        color_cols = ["季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)", "近20日法人買賣超(張數)"]
        format_dict = {c: "{:.2f}" for c in ["現價", "季乖離", "年乖離", "月營收MoM(%)", "月營收YoY(%)", "今年以來累積營收YoY(%)"]}
        format_dict["近20日法人買賣超(張數)"] = "{:,.0f}"
        if "轉折值" in df.columns: 
            display_cols.append("轉折值"); format_dict["轉折值"] = "{:.2f}"
        styled_df = df[display_cols].style.apply(highlight_pivot, axis=1).format(format_dict, na_rep="-").map(color_tw, subset=color_cols)
    else:
        # 渲染 B/C 策略表格
        if "B." in strategy_choice:
            display_cols = ['股價代號', '公司名稱', '產業別', '現價', '240日報酬(%)', '20日報酬(%)', '近20日法人買賣超(張)']
            df_display = df[display_cols].copy()
            color_cols = ["240日報酬(%)", "20日報酬(%)"]
        else:
            chip_col = [c for c in df.columns if '法人' in c or '買超' in c][0]
            display_cols = ['股價代號', '公司名稱', '產業別', '現價', '今年以來累積營收YoY(%)', '240日報酬(%)', '20日報酬(%)', chip_col]
            df_display = df[display_cols].copy()
            color_cols = ['今年以來累積營收YoY(%)', '240日報酬(%)', '20日報酬(%)', chip_col]
        if "轉折值" in df.columns:
            display_cols.append("轉折值"); df_display = df[display_cols].copy(); color_cols.append("轉折值")
        styled_df = df_display.style.apply(highlight_pivot, axis=1).format({c: "{:.2f}" for c in df_display.columns if c not in ["股價代號", "公司名稱", "產業別", "近20日法人買賣超(張)"]}, na_rep="-").map(color_tech_blue, subset=color_cols)

    st.dataframe(styled_df, use_container_width=True)

    st.markdown('''
        <div class="disclaimer-box">
            <div class="disclaimer-icon">🛡️</div>
            <div class="disclaimer-text">
                <span class="disclaimer-bold">重要免責聲明 (Legal Disclaimer)</span>
                本系統篩選結果為大數據與量化模型之運算產出，內容僅供投資參考，不構成任何買賣建議或進出場依據。市場投資具有高度風險，使用者應進行獨立評估並做好個人資金與風險控管，本系統對任何投資損失不負法律責任。
            </div>
        </div>
    ''', unsafe_allow_html=True)
    
    st.download_button("📥 下載 Excel 數據報告", df.to_csv(index=False).encode('utf-8-sig'), file_name=f"Quant_Report_{data_date}.csv")

st.divider(); st.caption("QUANTUM DATA SYSTEM © 2026 | Design IG:chiafeimao")
