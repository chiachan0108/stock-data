_, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🚀 啟動AI量化篩選", use_container_width=True):
            
            # 💡 依據不同策略動態生成專屬 15 秒掃描文案與終端風格
            if "A." in strategy_choice:
                status_title = "🧬 AI 營收動能引擎執行深度掃描..."
                steps = [
                    (20, "🔍 掃描電子產業長線多頭排列...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>鎖定 MA60 > MA240 技術位階...</span>"),
                    (40, "🏭 深度運算 5 年 LTM 營收成長曲線...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>營收規模創高驗證完成...</span>"),
                    (60, "⚡ 驗證 YoY 雙重成長與財務護城河...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>排除短期營收動能衰退標的...</span>"),
                    (80, "🏦 疊加近 20 日三大法人籌碼狀態...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>籌碼集中度與聰明錢分析完成...</span>"),
                    (100, "🏆 彙整基本面極端強勢名單...", "<span style='color:#00f2ff; font-family:monospace;'>[SYSTEM]</span> <span style='color:#e2e8f0; font-weight:600;'>量子運算結束，準備解構數據...</span>")
                ]
            elif "B." in strategy_choice:
                status_title = "🚀 AI 股價動能引擎執行深度掃描..."
                steps = [
                    (20, "🌊 過濾全市場流動性與非普通股標的...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>排除 ETF、權證及低流動性標的...</span>"),
                    (40, "📈 展開 240 日與 20 日雙週期報酬計算...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>動能基準線與歷史波動率建立中...</span>"),
                    (60, "⚔️ 對標大盤績效進行 Alpha 值剔除...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>已鎖定具備相對超額報酬之標的...</span>"),
                    (80, "🏦 追蹤聰明錢流向與主力籌碼堆疊...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>法人淨買超狀態確認完成...</span>"),
                    (100, "🏆 彙整技術面極端強勢名單...", "<span style='color:#00f2ff; font-family:monospace;'>[SYSTEM]</span> <span style='color:#e2e8f0; font-weight:600;'>量子運算結束，準備解構數據...</span>")
                ]
            else:
                status_title = "🌌 量子雙引擎交集模組執行深度掃描..."
                steps = [
                    (20, "🧬 同步載入 [模組 A] 與 [模組 B] 底層數據...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>雙軌運算資料庫建立完成...</span>"),
                    (40, "⚡ 執行營收創高與相對強勢碰撞測試...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>核心條件交集過濾進行中...</span>"),
                    (60, "👑 提取雙重吻合之極端強勢標的...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>勝率模型收斂，剔除單邊弱勢股...</span>"),
                    (80, "🏦 進行最終法人籌碼雙重認證...", "<span style='color:#00f2ff; font-family:monospace;'>[SUCCESS]</span> <span style='color:#94a3b8;'>聰明錢長短線佈局過濾完成...</span>"),
                    (100, "🏆 彙整雙引擎最終交集名單...", "<span style='color:#00f2ff; font-family:monospace;'>[SYSTEM]</span> <span style='color:#e2e8f0; font-weight:600;'>量子運算結束，準備解構數據...</span>")
                ]

            p_bar = st.progress(0, text="📡 正在初始化數據終端...")
            with st.status(status_title, expanded=True) as status:
                for progress_val, bar_text, status_msg in steps:
                    time.sleep(3) # 每個階段耗時 3 秒，總共 15 秒儀式感
                    p_bar.progress(progress_val, text=bar_text)
                    status.markdown(status_msg, unsafe_allow_html=True)
                
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
