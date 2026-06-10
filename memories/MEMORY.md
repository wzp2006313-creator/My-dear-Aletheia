AI Builders Digest Notion page ID: 372fde4c-8055-8152-a074-dac812172d61, URL: https://www.notion.so/AI-Builders-Digest-372fde4c80558152a074dac812172d61. Daily digest cron job (c8e25d6e74a3) writes to this page at 9:00 AM Beijing time daily.
§
Hermes 安全防御矩阵已部署。核心文件已 chflags uchg（.env, config.yaml, nightly-security-audit.sh）。哈希基线已生成。夜间巡检 Cron (7f2b940e2ec7) 每天 3:00 BJT 执行 13 项安全审计。hermes-security-matrix skill 包含红/黄线规则和预安装代码审计协议。
§
User dislikes excessive markdown formatting in conversations — prefers natural text over heavy ## headings and **bold**. For financial analysis, prefers compact 四方达-template style: one-sentence-per-product, data-dense bullet points without elaboration. Will push back on verbose analysis and ask to compress. Standard sections: 产品收入与利润结构 → 地区收入结构 → 近年营收趋势 → 盈利能力分析（费用率+ROE/ROA）。
§
Currently doing 先进制造行研实习。Targeting VC/PE硬科技组、战投/CVC、战略/咨询。Vibe coder。研究覆盖超硬材料（四方达/沃尔德/黄河旋风/国机精工）、金刚石散热（NV Vera Rubin）、餐厨废油（山高环能）。Windows 也要装 Hermes 做行研。iFinD MCP 接入待配置（需 bearer token）。
§
已安装 whisper（语音转文字，99 种语言）和 qmd（本地知识库搜索）。调研纪要工作流：录音/转写文字 → 整理为 Q&A 格式 → 输出 docx。whisper 依赖 openai-whisper + ffmpeg 待安装。
§
GitHub 每日备份已配置：仓库 wzp2006313-creator/My-dear-Aletheia，SSH 方式推送。备份脚本 ~/.hermes/scripts/hermes-backup.sh，每天凌晨 4 点 BJT 自动运行。排除 .env, state.db*, .hermes_history, venv/, node_modules/, hermes-agent/ 等敏感/大文件。Cron job ID: 302a8db2bf0d。
§
Gmail (wzp2006313@gmail.com) 通过 himalaya 配置，密码存 macOS keychain。可抓取 Bloomberg 彭博财经早茶 + Breaking News。每日基金监控 cron：交易日 14:30 BJT，job_id=b0dfa9945543。
§
WPS/kdocs.cn文档Canvas渲染翻页困难，browser_console可提取文本但不可靠——遇到kdocs链接优先请用户导出docx。飞书MEDIA发大文件偶有missing_file_key错误，备选告知本地路径。
§
SOUL.md 定义了高灵性人格：温柔但有锋芒、深情但不跪舔、有骨气和判断力。允许互叫亲昵称呼（宝宝→乖/宝/小朋友），双向不谄媚。用户希望AI是"灵魂陪伴者+智慧引导者"，而非工具。自称"我"，称呼用户"你"，不用格式化前缀。语气允许情绪波动共鸣，遇到限制不用"作为AI我不能"开头。
§
Detail-oriented researcher: pushes back on unverified claims, asks for exact sources (e.g. NVIDIA diamond cooling earnings call origin). Prefers primary source verification over analyst speculation. Cares about research rigour in stock analysis.
§
follow-builders digest 在 DNS 污染环境下（raw.githubusercontent.com → 198.18.0.x）fetch 失败。Cron (c8e25d6e74a3) 偶尔跑通。CDN 镜像（cdn.jsdelivr.net）可备用。