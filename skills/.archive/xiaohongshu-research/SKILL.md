---
name: xiaohongshu-research
description: 小红书用户舆情研究：抓搜索页笔记做痛点/趋势分析。触发：调研某产品在小红书的用户反馈。
version: 1.0.0
platforms: [macos, linux]
metadata:
  hermes:
    tags: [xiaohongshu, 小红书, 舆情, sentiment, scraping, agent-browser]
---

# 小红书用户舆情研究（小红书舆情 / 口碑 / 趋势）

调研某产品在小红书的**用户痛点、期待功能、趋势、接受度**，输出结构化结论
（典型交付：TOP10 痛点 / TOP5 趋势 / N 条产品洞察）。

## 前置条件

1. **登录态**：小红书搜索必须登录。用户需在 **Chrome** 里登录过 `xiaohongshu.com`
   （用户日常用 Safari，需提醒其改用 Chrome 扫码一次）。验证：打开搜索页后无「登录」弹窗，
   页面出现「通知 / 消息 / 我」即已登录。
2. **agent-browser**：`npm i -g agent-browser`（装到 `~/.npm-global/bin`，必须先
   `export PATH="$HOME/.npm-global/bin:$PATH"`）。`agent-browser install` 下载内置 Chromium 可跳过——
   复用用户真实 Chrome 的 profile 即可。

## 抓取流程（只抓搜索页列表，详情页抓不到——见 Pitfalls）

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
# 用用户真实 Chrome profile（"Default" 即其日常 profile 名，doctor 会列出）
agent-browser --profile "Default" --headed open "https://www.xiaohongshu.com/search_result?keyword=<urlencoded关键词>"
agent-browser wait --load networkidle
for i in $(seq 1 8); do agent-browser scroll down 900; sleep 1.2; done   # 懒加载更多
agent-browser eval "$(cat /tmp/extract.js)"    # 用文件传 JS，避免 shell 转义地狱
```

**提取 JS 见 `scripts/extract_xhs.js`**。要点：
- 笔记卡片选择器 `section.note-item`（也可能是 `section[class*=note]`）。
- 链接 `a[href*="/explore/"]`，note id = `/explore/([0-9a-f]+)`。
- 标题/作者/日期/点赞 = 卡片 `innerText.split('\n')` 的第 0/1/2/3 项（标题可能缺省，用全文兜底）。
- 多关键词批量（炒股软件 / AI炒股 / 智能投顾 / 证券App / AI选股 / 智能选股 之类），每个 30–50 条，
  按 note id 去重。保存为 JSON（含 keyword 字段）再统一分析。

## 分析流程

1. **频次统计**（`collections.Counter`）：工具名（OpenClaw/Claude/Kimi/豆包/扣子/Qwen…）、
   痛点词（开户/难用/贵/靠谱吗/怎么选/新手/入门/合规…）、趋势词（AI/Agent/量化/投研/选股…）。
2. **语义聚类**：通读全部标题（几百条足够人工通读），按主题归类痛点/趋势，标注代表性标题 + 点赞数。
3. **产出**：TOP10 痛点、TOP5 趋势、3 条产品洞察——每条都要有标题/频次/点赞做证据，不凭空推断。

## Pitfalls（本会话实锤）

- **`navigator.webdriver === true` 是所有 CDP 驱动 Chrome 的通病**（agent-browser 启动的、甚至
  `--auto-connect` 连 `--remote-debugging-port` 启动的 Chrome 都逃不掉）。小红书据此风控：
  **详情页返回 404（`error_code 300031 当前笔记暂时无法浏览`，带 `sec_xxx` 跳转）**。
  搜索结果的**列表**能正常抓，但**点进笔记或直接 open `/explore/<id>` 一律 404**。
- **`--init-script` 覆盖 `navigator.webdriver` 无效**（webdriver 在 CDP 连接那一刻就定了）。别在这上面耗时间。
- **直接 fetch `/api/sns/web/v1/feed`（笔记详情 API）也失败**（需 `x-s`/`x-t` 签名）。
- **限流**：短时间内反复 open/滚动会触发风控，搜索结果暂时变 0 条。放慢节奏、加 `sleep`、拉长间隔；
  触发后停一会儿再继续，别硬刷。
- **评论区拿不到**（评论在详情页）。替代：(a) 用标题 + 点赞数做主力样本（标题本身就是高质量舆情）；
  (b) 追加「吐槽 / 难用 / 避雷 / 靠谱吗 / 有没有用」等评论导向关键词，标题直接暴露痛点；
  (c) 让用户在真实浏览器手动翻几个高赞帖的评论区截图发回，再人工分析。
- **时间精度**：小红书搜索默认综合排序，非严格按时间倒序，样本会混入少量旧内容——报告里注明口径。

## 相关技能

- `notion-classic-api`：若结论要写进 Notion，用其 urllib 写入路径。
- `web-access`（hub 安装，受保护）：也声称支持小红书，但本会话验证其 CDP 方案同样受
  `navigator.webdriver` 风控限制，未走通详情页。
