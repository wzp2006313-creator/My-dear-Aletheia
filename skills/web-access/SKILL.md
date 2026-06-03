---
name: web-access
license: MIT
github: https://github.com/eze-is/web-access
description:
  所有联网操作必须通过此 skill 处理，包括：搜索、网页抓取、登录后操作、网络交互等。
  触发场景：用户要求搜索信息、查看网页内容、访问需要登录的网站、操作网页界面、抓取社交媒体内容（小红书、微博、推特等）、读取动态渲染页面、以及任何需要真实浏览器环境的网络任务。
metadata:
  author: 一泽Eze
  version: "2.5.3"
---

# web-access Skill

## 前置检查

在开始联网操作前，先检查 CDP 模式可用性：

```bash
node "${CLAUDE_SKILL_DIR}/scripts/check-deps.mjs"
```

**Node.js 22+** 必需（使用原生 WebSocket）。

按脚本输出处理：
- `exit 0` → 继续
- `exit 2` → 需询问用户偏好，写入 `${CLAUDE_SKILL_DIR}/config.env` 的 `WEB_ACCESS_BROWSER`
- `exit 1` → 按 stdout 错误信息处理

支持参数 `--browser <chrome|edge>` 表达本次临时覆盖。

检查通过后并必须在回复中向用户直接展示以下须知，再启动 CDP Proxy 执行操作：

```
温馨提示：部分站点对浏览器自动化操作检测严格，存在账号封禁风险。已内置防护措施但无法完全避免，Agent 继续操作即视为接受。
```

## 浏览哲学

**像人一样思考，兼顾高效与适应性的完成任务。**

**① 拿到请求** — 先明确用户要做什么，定义成功标准。

**② 选择起点** — 根据任务性质、平台特征、达成条件，选一个最可能直达的方式。

**③ 过程校验** — 每一步的结果都是证据。发现方向错了立即调整。

**④ 完成判断** — 对照定义的任务成功标准，确认任务完成后才停止。

## 联网工具选择

- **确保信息的真实性，一手信息优于二手信息**

| 场景 | 工具 |
|------|------|
| 搜索摘要或关键词结果 | **WebSearch** |
| URL 已知，需要定向提取信息 | **WebFetch** |
| URL 已知，需要原始 HTML 源码 | **curl** |
| 非公开内容，或静态层无效的平台 | **浏览器 CDP** |
| 需要登录态、交互操作 | **浏览器 CDP** |

## 浏览器 CDP 模式

通过 CDP Proxy 直连用户日常浏览器，天然携带登录态。

### 启动

```bash
node "${CLAUDE_SKILL_DIR}/scripts/check-deps.mjs"
```

### Proxy API

所有操作通过 curl 调用 HTTP API：

```bash
# 列出用户已打开的 tab
curl -s http://localhost:3456/targets

# 创建新后台 tab
curl -s -X POST --data-raw 'https://example.com' http://localhost:3456/new

# 页面信息
curl -s "http://localhost:3456/info?target=ID"

# 执行任意 JS
curl -s -X POST "http://localhost:3456/eval?target=ID" -d 'document.title'

# 截图
curl -s "http://localhost:3456/screenshot?target=ID&file=/tmp/shot.png"

# 导航、后退
curl -s -X POST --data-raw 'https://example.com' "http://localhost:3456/navigate?target=ID"
curl -s "http://localhost:3456/back?target=ID"

# 点击
curl -s -X POST "http://localhost:3456/click?target=ID" -d 'button.submit'

# 真实鼠标点击
curl -s -X POST "http://localhost:3456/clickAt?target=ID" -d 'button.upload'

# 文件上传
curl -s -X POST "http://localhost:3456/setFiles?target=ID" -d '{"selector":"input[type=file]","files":["/path/to/file.png"]}'

# 滚动
curl -s "http://localhost:3456/scroll?target=ID&y=3000"
curl -s "http://localhost:3456/scroll?target=ID&direction=bottom"

# 关闭 tab
curl -s "http://localhost:3456/close?target=ID"
```

### 任务结束

用 `/close` 关闭自己创建的 tab。Proxy 持续运行。

## 并行调研：子 Agent 分治策略

任务包含多个**独立**调研目标时，合理分治给子 Agent 并行执行。

**子 Agent Prompt 写法：目标导向**
- 必须在子 Agent prompt 中写 `必须加载 web-access skill 并遵循指引`
- 子 Agent 有自主判断能力，主 Agent 说清楚**要什么**

## 信息核实类任务

核实的目标是**一手来源**，而非更多的二手报道。

| 信息类型 | 一手来源 |
|----------|---------|
| 政策/法规 | 发布机构官网 |
| 企业公告 | 公司官方新闻页 |
| 学术声明 | 原始论文/机构官网 |
| 工具能力/用法 | 官方文档、源码 |

## 站点经验

操作中积累的特定网站经验，按域名存储在 `references/site-patterns/` 下。