import streamlit as st
import pandas as pd
import datetime, io, time, requests

# =============================================================================
# [配置區]
# =============================================================================
RAW_URL = "https://raw.githubusercontent.com/chiachan0108/stock-data/refs/heads/main/daily_result.csv"

# =============================================================================
# [1. 頁面配置與 高階簡約 CSS]
# =============================================================================
st.set_page_config(page_title="QUANTUM TECH SCANNER", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=JetBrains+Mono:wght@400;700&display=swap');
    
    html, body, [class*="css"] { 
        font-family: 'Inter', sans-serif; 
        background-color: #0e1117;
        color: #e0e0e0;
    }

    .main-title {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        letter-spacing: -1.5px;
        color: #ffffff;
        font-size: 3rem;
        margin-bottom: 5px;
    }

    .update-note {
        font-size: 0.95rem;
        color: #888888;
        background: rgba(255, 255, 255, 0.03);
        padding: 8px 15px;
        border-radius: 50px;
        display: inline-block;
        margin-bottom: 25px;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }

    .logic-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
        gap: 16px;
        margin-bottom: 30px;
    }

    .logic-item {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(0, 242, 255, 0.15);
        border-radius: 14px;
        padding: 24px;
        transition: all 0.4s ease;
    }

    .logic-index { font-family: 'JetBrains Mono', monospace; font-size: 1rem; color: #00f2ff; font-weight: 700; margin-bottom: 12px; }
    .logic-subtitle { font-size: 1.1rem; font-weight: 700; color: #ffffff; margin-bottom: 8px; }
    .logic-desc { font-size: 0.95rem; color: #a0a0a0; line-height: 1.6; }
    .highlight { color: #00f2ff; font-weight: 700; }
    
    .stProgress > div > div > div > div { background: linear-gradient(to right, #00f2ff, #0072ff); height: 8px; }
    </style>
""", unsafe_allow_html=True)

if 'scan_completed' not in st.session_state:
    st.session_state['scan_completed'] = False

# =============================================================================
# [2. 主介面設計]
# =============================================================================

# 標題與公告
st.markdown('<h1 class="main-title">🛡️ QUANTUM SCANNER</h1>', unsafe_allow_html=True)
st.markdown('<div class="update-note">🕒 數據公告：每日 20:00 定時更新資料庫</div>', unsafe_allow_html=True)
st.markdown("---")

if not st.session_state['scan_completed']:
    st.markdown("### 系統核心邏輯 | SYSTEM ARCHITECTURE")
    
    # 核心邏輯 - 使用您指定的文字內容
    logic_html = """
    <div class="logic-grid">
        <div class="logic-item">
            <div class="logic-index">01 / SCOPE</div><div class="logic-subtitle">選股範圍</div>
            <div class="logic-desc">鎖定台灣全體上市櫃<span class="highlight">電子產業</span>標的。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">02 / LIQUIDITY</div><div class="logic-subtitle">流動性門檻</div>
            <div class="logic-desc">近20日平均日成交量需大於 <span class="highlight">1,000張</span>。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">03 / LEVEL</div><div class="logic-subtitle">技術位階</div>
            <div class="logic-desc">股價需穩健站於長線生命線 <span class="highlight">MA240</span> 之上。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">04 / TREND</div><div class="logic-subtitle">趨勢排列</div>
            <div class="logic-desc"><span class="highlight">MA60 > MA240</span>，呈現中長線多頭排列。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">05 / SCALE</div><div class="logic-subtitle">營收規模</div>
            <div class="logic-desc">近12個月累積營收 (<span class="highlight">LTM</span>) 創下5年來最高紀錄。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">06 / MOMENTUM</div><div class="logic-subtitle">創高動能</div>
            <div class="logic-desc">近6個月內至少有1個月以上的營收創下 <span class="highlight">歷史新高</span>。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">07 / DYNAMICS</div><div class="logic-subtitle">季度動能</div>
            <div class="logic-desc">確保 <span class="highlight">近1季YoY > 0</span>，營運動能持續擴張。</div>
        </div>
        <div class="logic-item">
            <div class="logic-index">08 / TRACKING</div><div class="logic-subtitle">相對強弱判定</div>
            <div class="logic-desc">更新三大法人籌碼並 <span class="highlight">判定相對大盤強弱</span> 。</div>
        </div>
    </div>
    """
    st.markdown(logic_html, unsafe_allow_html=True)

    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🚀 啟動全量量化掃描系統", type="primary", use_container_width=True):
            p_bar = st.progress(0, text="📡 正在初始化系統終端...")
            with st.status("正在執行深度分析...", expanded=True) as status:
                steps = [(20, "🔍 過濾標的..."), (40, "📈 計算均線..."), (60, "🏭 檢索營收..."), (80, "👥 同步籌碼..."), (100, "🏆 產出報告...")]
                for p, txt in steps:
                    time.sleep(1.5)
                    p_bar.progress(p, text=txt)
                    status.write(txt)
                try:
                    r = requests.get(f"{RAW_URL}?t={int(time.time())}", timeout=10)
                    if r.status_code == 200:
                        df = pd.read_csv(io.StringIO(r.text), on_bad_lines='skip')
                        st.session_state['temp_df'] = df
                        st.session_state['scan_completed'] = True
                        status.update(label="✅ 分析完成", state="complete", expanded=False)
                        st.balloons(); st.rerun()
                except Exception: st.error("數據同步中，請稍後再試。")

else:
    # --- 結果頁面：日期智慧判斷 ---
    df = st.session_state['temp_df']
    
    # 台北時區校正
    tz_delta = datetime.timedelta(hours=8)
    now_taipei = datetime.datetime.utcnow() + tz_delta
    
    # 晚上 8 點前顯示昨日，8 點後顯示今日
    if not df.empty and '更新日期' in df.columns:
        update_date = df['更新日期'].iloc[0]
    else:
        if now_taipei.hour < 20:
            update_date = (now_taipei - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            update_date = now_taipei.strftime('%Y-%m-%d')
    
    m1, m2, m3 = st.columns(3)
    m1.metric("今日掃描樣本", "900+ 檔")
    m2.metric("符合門檻標的", f"{len(df)} 檔")
    m3.metric("數據最後更新", str(update_date))
    
    st.sidebar.button("🔄 重新啟動掃描", on_click=lambda: st.session_state.update({"scan_completed": False}))
    
    st.subheader(f"🏆 QUANTUM TOP PICKS")
    
    if not df.empty:
        styled = df.style
        if '年乖離(%)' in df.columns: styled = styled.background_gradient(subset=['年乖離(%)'], cmap='RdYlGn_r')
        if '近5日三大法人買賣超(張數)' in df.columns: styled = styled.background_gradient(subset=['近5日三大法人買賣超(張數)'], cmap='Greens')
        if '近一季相對大盤強弱' in df.columns: styled = styled.background_gradient(subset=['近一季相對大盤強弱'], cmap='RdYlGn')

        st.dataframe(styled.format({
            "現價": "{:.2f}", "季乖離(%)": "{:.2f}%", "年乖離(%)": "{:.2f}%", 
            "近一季相對大盤強弱": "{:+.2f}%", "營收YoY(%)": "{:.2f}%", "營收MoM(%)": "{:.2f}%"
        }, na_rep="-"), use_container_width=True)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.sidebar.download_button("📥 下載 Excel 完整報告", output.getvalue(), file_name=f"Quant_Report_{update_date}.xlsx")

st.divider()
st.caption("QUANTUM DATA SYSTEM © 2026 | Minimalist Design. Maximum Insight.")
