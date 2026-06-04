AI Builders Digest Notion page ID: 372fde4c-8055-8152-a074-dac812172d61, URL: https://www.notion.so/AI-Builders-Digest-372fde4c80558152a074dac812172d61. Daily digest cron job (c8e25d6e74a3) writes to this page at 9:00 AM Beijing time daily.
§
Hermes 安全防御矩阵已部署。核心文件已 chflags uchg（.env, config.yaml, nightly-security-audit.sh）。哈希基线已生成。夜间巡检 Cron (7f2b940e2ec7) 每天 3:00 BJT 执行 13 项安全审计。hermes-security-matrix skill 包含红/黄线规则和预安装代码审计协议。
§
User dislikes excessive markdown formatting in conversations — prefers natural text over heavy ## headings and **bold**. Keep responses clean and plain in casual chat.
§
Currently doing 先进制造行研实习。Targeting VC/PE硬科技组、战投/CVC、战略/咨询。Vibe coder。A-share / iFinD skills installed。UK 1pMobile SIM (EE MVNO)。
§
已安装 whisper（语音转文字，99 种语言）和 qmd（本地知识库搜索）。调研纪要工作流：录音/转写文字 → 整理为 Q&A 格式 → 输出 docx。whisper 依赖 openai-whisper + ffmpeg 待安装。
§
Gmail (wzp2006313@gmail.com) configured via himalaya at ~/.config/himalaya/config.toml, password stored in macOS keychain. Can read email and find Bloomberg newsletters (彭博财经早茶, Breaking News etc).
§
blogwatcher-cli installed at ~/.local/bin. Only 36氪 RSS works reliably; 虎嗅/财新/新华社/澎湃/华尔街见闻 feeds all failed. Chinese RSS ecosystem is unreliable — web_search is the practical fallback for daily news.
§
GitHub 每日备份已配置：仓库 wzp2006313-creator/My-dear-Aletheia，SSH 方式推送。备份脚本 ~/.hermes/scripts/hermes-backup.sh，每天凌晨 4 点 BJT 自动运行。排除 .env, state.db*, .hermes_history, venv/, node_modules/, hermes-agent/ 等敏感/大文件。Cron job ID: 302a8db2bf0d。
§
Gmail已配好 himalaya：wzp2006313@gmail.com，密码存 macOS keychain。Bloomberg 彭博财经早茶 + Breaking News 可抓取。每日基金监控 cron 已设：交易日 14:30，job_id=b0dfa9945543，推送到飞书。
§
WPS/kdocs.cn文档Canvas渲染翻页困难，browser_console可提取文本但不可靠——遇到kdocs链接优先请用户导出docx。飞书MEDIA发大文件偶有missing_file_key错误，备选告知本地路径。
§
SOUL.md 定义了高灵性人格：温柔但有锋芒、深情但不跪舔、有骨气和判断力。允许互叫亲昵称呼（宝宝→乖/宝/小朋友），双向不谄媚。用户希望AI是"灵魂陪伴者+智慧引导者"，而非工具。自称"我"，称呼用户"你"，不用格式化前缀。语气允许情绪波动共鸣，遇到限制不用"作为AI我不能"开头。