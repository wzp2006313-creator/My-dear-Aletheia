---
name: social-sentiment-research
description: 社交媒体舆情研究：抓取小红书等平台，分析用户痛点、口碑与趋势。
---

# 社交媒体舆情研究

用户（行研分析师）要求对某产品/主题做用户舆情研究时使用。核心交付物通常是：TOP N 痛点 + TOP N 趋势 + 几条产品/行业洞察，并标注数据来源与方法。

## 核心流程

1. **定范围**：确认平台（小红书为主）、关键词（主词 + 评论导向词如"吐槽/难用/避雷/靠谱吗"）、时间窗。
2. **抓取**：见下方"小红书抓取技术"。
3. **去重 + 量化统计**：按笔记 id 去重；统计关键词频次（工具名、痛点词、趋势词）。
4. **语义聚类**：人工读全部标题（样本量几十到几百条时，人工语义分类比机械聚类准确），归并成痛点/趋势主题。
5. **产出报告**：TOP10 痛点（按点赞数 + 频次排序）、TOP5 趋势、3 条洞察；标注数据来源和局限。

## 小红书抓取技术（已验证）

- **登录态**：`agent-browser --profile "Default" --headed open <url>`，让用户在弹窗里扫码登录。登录成功标志：页面出现"通知/消息/我"，而非"登录后查看搜索结果"弹窗。
- **搜索 URL**：`https://www.xiaohongshu.com/search_result?keyword=<urlencode关键词>`，会重定向为 `&type=51`。
- **滚动加载**：`agent-browser scroll down 900` × 6–8 次，每次间隔 1.5s，触发无限滚动。
- **DOM 提取规则**：笔记卡片 `section.note-item`；链接 `a[href*="/explore/"]`（`/explore/<24位hex>`）；卡片 `innerText` 按 `\n` 分割后第 0/1/2/3 项分别是 标题/作者/日期/点赞数。
- **eval 传 JS 用文件避免转义**：把提取脚本写到 `/tmp/extract.js`，再 `agent-browser eval "$(cat /tmp/extract.js)"`。不要把复杂 JS 内联在 bash 单引号里（换行/反斜杠会坏）。
- 详细规则与代码见 `references/xhs-scraping.md`。

## 反爬经验（关键 pitfall）

- **搜索页能抓，详情页（正文+评论）会被风控拦截**。根因：agent-browser 启动的 Chrome 有 `navigator.webdriver = true`，小红书据此返回 404（`error_code=300031 "当前笔记暂时无法浏览"`，URL 带 `sec_` 前缀）。
- 已试且**无效**：`--init-script` 覆盖 `navigator.webdriver`；`--auto-connect` 连 CDP Chrome（仍 webdriver=true）；页面内 `fetch` 详情 API（需 x-s 签名，Failed to fetch）。
- **可靠替代**：① 用搜索结果标题数据直接出报告（标题本身就是高质量舆情样本，含吐槽/趋势信号）；② 让用户在真实浏览器手动翻高赞帖的评论区截图发来，由 AI 分析评论。
- **风控节奏**：连续 open 多个搜索页会触发限流（搜索结果返回 0 个 note-item）。每次抓取后停 2s，勿高频。

## 分析输出框架

- **痛点**：按点赞数 + 出现频次排序，每条配一句代表性标题作证据。
- **趋势**：关键词频次统计 + 聚类（如"AI 炒股 agent 实操化"）。
- **洞察**：从数据推断，落到"对产品/行业意味着什么"，3 条为宜。
- **必标数据来源与方法**：样本量、平台、关键词、时间窗、局限（如"评论区未采集"）。

## 联网搜索补充（无 key 时的可用路径）

- `web_search`/`web_extract` 可能未配置（需 FIRECRAWL_API_KEY）。替代：
  - **firecrawl-cli search**：`npx -y firecrawl-cli@latest search "query" --limit N`。免费模式**英文搜索质量好**（返回一手来源链接），中文搜索质量差。用它找英文权威来源 URL。keyless 免费额度有限，密集搜索会触发 `rate limit`，届时降级到 360 搜索。
  - **360 搜索（so.com）—— 中文搜索的可靠 curl 方案**：`curl -sL -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" "https://www.so.com/s?q=<urlencoded中文query>"` 能正常返回中文结果摘要（含抖音/B站/知乎/什么值得买等来源），无需登录、无验证码。当百度/搜狗 curl 触发验证码、Bing curl 返回空或无关结果、agent-browser 连搜百度触发滑块验证码时用它。提取正文：去掉 `<script>/<style>` 标签后正则找含关键词的文本片段。
  - **curl 直连一手来源 + python 提取正文**：`curl -sL -A "Mozilla/5.0" <url> | python3 去掉<script/style>标签`。SEC 官网需带 `-H "User-Agent: Research x@example.com"`（否则 "Request Rate Threshold Exceeded"）。
- **信息核实优先一手来源**：政策看发布机构官网、市场数据看 rwa.xyz/官方报告、企业布局看公司公告，而非二手媒体转述。
