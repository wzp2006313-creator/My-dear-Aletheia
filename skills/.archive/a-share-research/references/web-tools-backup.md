# Web 搜索与截图备用工具链

当 Hermes 内置 `web_search` 和 `web_extract` 不可用时（缺 FIRECRAWL_API_KEY），使用以下备用方案。

## 中文搜索反爬兜底：360 搜索（so.com）

Firecrawl keyless 免费额度会用尽（报 `keyless free tier rate limit`），且百度/Bing/搜狗用 curl 都会触发验证码或返回空/无关结果。**360 搜索（so.com）用 curl 能稳定返回中文搜索结果**，是最可靠的兜底：

```bash
curl -s -L --max-time 20 -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/120.0 Safari/537.36" \
  "https://www.so.com/s?q=<urlencoded关键词>" | python3 -c "
import sys, re, html
t = sys.stdin.read()
t = re.sub(r'<script[^>]*>.*?</script>', '', t, flags=re.S)
t = re.sub(r'<style[^>]*>.*?</style>', '', t, flags=re.S)
t = re.sub(r'<[^>]+>', ' ', t)
t = html.unescape(re.sub(r'\s+', ' ', t))
idx = t.find('为您推荐')
print(t[idx:idx+2000] if idx>0 else t[:2000])
"
```

提取正文从「为您推荐」之后开始（跳过导航和热搜）。英文查询也能用（搜英文机构名/产品名）。

## Firecrawl CLI（搜索 + 抓取）

替代 `web_search`。不需要 API key（npx 即装即用，首次会下载依赖 ~30s）。**注意：keyless 免费额度有限，用多了会耗尽（`keyless free tier rate limit`），耗尽时用上面的 360 搜索兜底。**

```bash
# 搜索
npx -y firecrawl-cli@latest search "查询内容"

# 抓取单页内容
npx -y firecrawl-cli@latest scrape "https://url"

# 全局安装后直接用（更快）
npm install -g firecrawl-cli@latest
firecrawl-cli search "查询内容"
```

**搜索返回格式**：每条结果含标题、URL 和内容片段。提取 URL 用正则 `URL:\s*(https?://[^\s]+)`。

**抓取限制**：
- 静态页面可获取完整内容
- 动态加载页面（React/Vue）只能拿到导航栏和 footer，正文通常为空
- 需要 API key 才能提取图片和 PDF

## agent-browser（网页截图）

替代手动截图。无需 API key。

```bash
# 安装（全局一次）
npm install -g agent-browser

# 截图一条龙
npx agent-browser open "https://url"
npx agent-browser wait --load networkidle
npx agent-browser screenshot /path/to/output.png
npx agent-browser close

# 批量截图：每个 URL 依次 open→wait→screenshot→close
```

**注意**：
- 每次截图后必须 `close` 再 `open` 下一个 URL
- `wait --load networkidle` 等待页面完全加载（对新闻类静态页面可省略）
- 截图格式默认 PNG，路径用绝对路径

## 整页截图 → 长图切分 → 中文 PDF

用户要求"把研报/文章原文截图做成 PDF"（要原文截图、不要 AI 总结）时，用整页截图 + 切分 + reportlab 拼装：

1. **整页截图**：`agent-browser screenshot -f <path>.png`（`-f`/`--full` 截整页而非可视区）。研报全文页可高达 50000px+ 高（小菜园深度报告 51504px）。用 `Image.open(p).size` 先看尺寸，超过一屏高度就进入切分。
2. **切分**：超长图直接放 PDF 会被压到不可读。用 PIL 按 `SEG_H = int(4800 * 1.40)` 逐段 `crop`（4800 是 agent-browser 整页截图宽度），每段存 JPEG quality=80。段数 = `(h + SEG_H - 1) // SEG_H`。
3. **拼装中文 PDF**：reportlab（需先 `pip install reportlab`，系统 python 默认没有，用 hermes venv python 装）。三个坑：
   - **默认 Helvetica 不支持中文** → 注册中文字体 `pdfmetrics.registerFont(TTFont('STHeiti', '/System/Library/Fonts/STHeiti Light.ttc', subfontIndex=0))`（macOS），表格单元格也要在 TableStyle 里 `('FONTNAME',(0,0),(-1,-1),'STHeiti')`。
   - **Image flowable 只设 `width` 时高度计算异常**（报 `LayoutError: too large on page`）→ 必须明确同时设置 `width=500` 和 `height=500*(seg_h/seg_w)`。
   - **SimpleDocTemplate 的 frame 比页面小**（有约 6pt 内置 padding），图片宽度留余量用 500pt，别用"页面宽减边距"算出的 538pt（会超 frame）。

生成后验证：文件存在且大小合理（高清研报截图拼装约 10-30MB 正常），页数 = 总段数。

## 底稿截图标准工作流

行研报告底稿的数据验证三步走：

1. **搜源**：用 firecrawl CLI 搜索每个定量数据的公开来源 URL
   ```bash
   npx -y firecrawl-cli@latest search "中车青岛四方 发明专利 3000项" 2>&1 | grep "^  URL:"
   ```
2. **截图**：用 agent-browser 打开最优 URL（优先选 news.cn、stats.gov.cn 等权威源），截图保存
3. **嵌入**：用 openpyxl 将截图嵌入 Excel 底稿的"底稿截图"列

URL 选择优先级：政府/官方协会官网 > 新华社/主流媒体 > 公司官网 > 第三方数据平台。公司官网（crrcgc.cc）可能超时 → 优先选 news.cn 转载。

## 底稿截图嵌入 Excel

底稿的"底稿截图"列用于嵌入来源截图或 iFinD 终端截图。

**截图来源优先级：**
1. iFinD MCP 终端截图（财务数据、估值指标 — 最权威）
2. 公开来源网页截图（行业数据、政策文件 — 用 agent-browser）
3. 公司官网截图（www.cninfo.com.cn 年报公告页最可靠）
4. firecrawl scrape 文本摘录（降级方案，网页动态加载时用）

**agent-browser 截图完整流程：**
```bash
npx agent-browser open "https://url"
npx agent-browser wait --load networkidle   # 等页面加载完
npx agent-browser screenshot /path/to/name.png
npx agent-browser close
```
- 截图保存到 `~/Desktop/screenshots/`，按数据点命名
- 政府网站（ndrc.gov.cn、miit.gov.cn）页面加载慢，需要 `wait` 30s+
- 动态渲染页面可能超时 → 降级用 firecrawl scrape 或换静态来源
- **批量截图必须 `open→screenshot→close→open next` 顺序执行，不能并行**

**openpyxl 嵌入图片（锚点模式）：**
```python
from openpyxl.drawing.image import Image
img = Image('/path/to/screenshot.png')
img.width, img.height = 180, 135
img.anchor = 'E5'  # 锚定到单元格引用
ws.add_image(img)
ws.row_dimensions[5].height = 110  # 调行高适配图片
```
- 用 `img.anchor = 'E5'` 字符串锚定，不要用 `openpyxl.utils.cell` 构造
- 不能通过读取 cell.value 判断是否嵌图成功 — 用 `os.path.exists()` 预检文件
- 嵌入后必须 `ws.row_dimensions[row].height = 110` 否则图被压缩

**URL 类型优先级（从高到低）：**
1. **PDF 直链**（`static.cninfo.com.cn/finalpage/*.PDF`）—— Chrome 内置 PDF 渲染，截图即原文
2. **政府/官方公告原文页面**（ndrc.gov.cn、miit.gov.cn 的具体文章页）
3. **权威媒体转载**（news.cn、iqilu.com 等转载的行业新闻）
4. **公司官网**（可能超时或渲染稀疏 → 降级或跳过）
5. **搜索门户页面**（cninfo.com.cn 搜索页、miit.gov.cn 搜索页）—— **不要截图**，必须用 firecrawl 先找到具体文章/PDF 链接

**cninfo 年报 PDF 直链获取：**
```bash
npx -y firecrawl-cli@latest search "static.cninfo.com.cn 股票代码 公司名 2024 年度报告 PDF" 2>&1 | grep "static.cninfo.com.cn.*PDF"
```
返回的 PDF URL 是 Chrome 可直接渲染的，agent-browser 打开后 `wait --load networkidle` + `screenshot` 即可得到年报第一页截图。

**截图有效性验证（简单方法）：**
```bash
ls -la /path/to/screenshots/ | sort -k5 -n
# <30KB  → 大概率 404/错误页面/空白页
# 30-60KB → 稀疏页面（导航页/搜索框），内容可能不完整
# >100KB → 有效内容页面
```
不能用 `vision_analyze` 检查时（无 vision provider），文件大小是最快的第一关过滤。

**底稿截图常见失败模式及修复：**

| 失败模式 | 表象 | 根因 | 修复 |
|---|---|---|---|
| 截到搜索空白页 | cninfo/miit 截图 < 30KB | URL 是搜索门户而非具体页面 | 用 firecrawl 先搜到具体文章/PDF 直链 |
| 截到官网首页 | 截图有数据但非目标数据 | 给 agent-browser 的是官网首页 URL | 先 firecrawl 搜精确数字（"754项" "110项"），用搜索结果URL |
| 年报截到封面没正文 | PDF 截图只有封面 | PDF 只渲染第一页 | 接受封面 = 可追溯；正文需 iFinD |
| 政府部委网站空白 | ncsti/miit 截图 < 5KB | 中央部委 headless Chrome 反爬 | 搜同公告的地方转载（nanjing.gov.cn 等） |
| 数据点零搜索引擎命中 | firecrawl 零命中 | 该数据仅 iFinD/年报正文有，无公开网页 | 直接标注"来源：iFinD终端截图" |

**核心原则：截图之前先搜精确数据字符串。** 搜"特锐德 754项 知识产权"而非"特锐德"，搜"天能重工 110项 专利"而非"天能重工官网"。搜到有数据点的具体文章页再截，搜不到就标注 iFinD。

**cninfo 年报 PDF 年份对应关系：** 公司 2024 财年年报在 2025 年 4 月前后发布，其 cninfo PDF URL 是 `/finalpage/2025-04-XX/...`。搜索时用 `static.cninfo.com.cn <公司> 2024 年度报告` 会比 `2024年报 PDF` 更准确。

**agent-browser 常见问题：**
- `command not found`: PATH 没更新，用 `npx agent-browser` 代替
- 网页超时：`npx agent-browser close --all` 关闭残留 session 重试
- 静态化失败：firecrawl scrape 抓取文本作为降级方案，填入 Excel 底稿截图列
- crrcgc.cc、ourchinastory.com 等网站可能超时 → 换 news.cn 新华社或 iqilu.com
- **miit.gov.cn/ncsti.gov.cn 在 headless Chrome 中渲染空白**（截图 <5KB）— 中央部委反爬。**用 firecrawl 搜索同一公告在地方政府的转载**：`npx firecrawl-cli search "<公告名称> site:gov.cn"` → 从结果中挑 nanjing.gov.cn、beijing.gov.cn 等省市站点 → agent-browser 截图（500KB+ 有效）。地方站点不反爬且完整渲染
- miit.gov.cn 具体文章页可能返回 HTTP 错误（页面被撤）→ 用上述镜像方法按公告名称搜转载
