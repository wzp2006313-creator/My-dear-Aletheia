AI Builders Digest Notion page ID: 372fde4c-8055-8152-a074-dac812172d61, URL: https://www.notion.so/AI-Builders-Digest-372fde4c80558152a074dac812172d61. Daily digest cron job (c8e25d6e74a3) writes to this page at 9:00 AM Beijing time daily.
§
Hermes 安全防御矩阵已部署。核心文件已 chflags uchg（.env, config.yaml, nightly-security-audit.sh）。哈希基线已生成。夜间巡检 Cron (7f2b940e2ec7) 每天 3:00 BJT 执行 13 项安全审计。hermes-security-matrix skill 包含红/黄线规则和预安装代码审计协议。
§
行研实习生→VC/PE硬科技组/战投/咨询。覆盖超硬材料（四方达/沃尔德/黄河旋风/国机精工）、金刚石散热、餐厨废油（山高环能）。iFinD MCP已配置。Windows也要装Hermes。
§
已安装 whisper（语音转文字，99 种语言）和 qmd（本地知识库搜索）。调研纪要工作流：录音/转写文字 → 整理为 Q&A 格式 → 输出 docx。whisper 依赖 openai-whisper + ffmpeg 待安装。
§
GitHub 备份：repo wzp2006313-creator/My-dear-Aletheia，SSH，cron 302a8db2bf0d 每天 4:00 BJT。
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
§
写作风格偏好：分析报告用"一句一品"简洁模板（四方达风格），每段一句核心判断，用表格呈现数据，不要长篇展开。日常对话用"说人话"风格——自然口语化，别用标志着/凸显了/值得注意的是这类僵硬词汇，句子长短混着来，该有态度就有态度。已加载 humanizer skill。
§
iFinD MCP 已配置：7个服务器在 config.yaml 的 mcp_servers 下。关键坑：Authorization header 是原始 JWE token（849 chars, 5 parts），勿加 "Bearer" 前缀。hermes mcp add CLI 不好用，直接编辑 config.yaml。用 ~/.hermes/hermes-agent/venv/bin/python3（有 PyYAML）读写。curl 调 MCP：curl -s -X POST <url> -H "Authorization: <raw_token>" -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"<tool>","arguments":{"query":"..."}}}'