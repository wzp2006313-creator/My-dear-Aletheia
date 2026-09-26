# 小红书抓取详细规则与代码

## 已验证可用的抓取脚本（搜索页）

### 提取脚本（写到 /tmp/extract.js）

```js
JSON.stringify([...document.querySelectorAll('section.note-item,section[class*=note]')].map(c=>{
  const a=c.querySelector('a[href*="/explore/"]');
  if(!a)return null;
  const m=(a.href.match(/explore\/([0-9a-f]+)/)||[])[1];
  if(!m)return null;
  const t=c.innerText.split('\n').filter(x=>x.trim());
  return {id:m,title:t[0]||'',author:t[1]||'',date:t[2]||'',like:t[3]||'',raw:c.innerText.slice(0,180).replace(/\n/g,' | ')};
}).filter(Boolean))
```

### 调用方式（文件传参避免转义地狱）

```bash
export PATH="$HOME/.npm-global/bin:$PATH"
agent-browser --profile "Default" --headed open "https://www.xiaohongshu.com/search_result?keyword=AI%E7%82%92%E8%82%A1"
sleep 4
for i in 1 2 3 4 5 6 7 8; do agent-browser scroll down 900; sleep 1.5; done
agent-browser eval "$(cat /tmp/extract.js)"   # 输出是转义 JSON 字符串，需 json.loads 两次
```

### 解析 eval 输出

agent-browser `eval` 返回的是**转义过的 JSON 字符串**（外层带引号），Python 侧处理：

```python
import json
s = out.strip()            # out 是 terminal 返回的 output
if s.startswith('"'):
    s = json.loads(s)      # 第一次去外层引号转义
notes = json.loads(s)      # 第二次解析成 list
```

## 卡片字段映射（已验证）

`section.note-item` 的 `innerText` 按 `\n` 分割：
- `[0]` 标题
- `[1]` 作者昵称
- `[2]` 日期（如 "04-14" 或 "2025-10-12"）
- `[3]` 点赞数（如 "740" 或 "1万"）

注意：有些卡片无标题（只有 emoji/昵称），提取时会拿到空 title，需过滤；"相关搜索" 区块也会被误抓（innerText 含 "相关搜索"），按 href 为空过滤即可。

## 登录态判断标志

- **未登录**：页面出现「登录后查看搜索结果」+ 弹窗（"可用 小红书 或 微信 扫码 / 手机号登录 / +86 / 获取验证码 / 登录"）。
- **已登录**：`read` 输出顶部出现「首页 / 通知 / 消息 / 我」，无登录墙弹窗。

## 详情页风控诊断（未解决，记录用）

- 直接 `open https://www.xiaohongshu.com/explore/<note_id>` 返回 404：
  `https://www.xiaohongshu.com/404?source=/404/sec_...&error_code=300031&error_msg=当前笔记暂时无法浏览`
- 从搜索页 `a.click()` 进入同样 404（带 referer 也无效）。
- 根因：`agent-browser eval "navigator.webdriver"` 返回 `true`。agent-browser 用 `--remote-debugging-port=0` 启动 Chrome，CDP 连接即设 webdriver=true。
- 尝试过的无效方案：
  - `--init-script /tmp/stealth.js`（`Object.defineProperty(navigator,'webdriver',{get:()=>false})`）—— 页面加载前覆盖无效，eval 后仍是 true。
  - `--auto-connect` 连命令行启动的 Chrome（`--remote-debugging-port=9222`）—— 仍 webdriver=true。
  - 页面内 `fetch('/api/sns/web/v1/feed', {method:'POST',...})` —— 需 x-s 签名，返回 Failed to fetch。
- **结论**：agent-browser 无法抓小红书详情页评论。评论数据需用户手动在真实浏览器截图，或用搜索页标题数据替代。

## 风控节奏提示

- 连续 open 多个搜索页（>5 个）会触发限流，之后搜索结果 `document.querySelectorAll('section.note-item').length` 返回 0。
- 缓解：每抓完一个关键词停 2s；若返回 0，等待 1–2 分钟再试。
