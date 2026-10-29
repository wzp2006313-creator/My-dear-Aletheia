---
name: a-share-research
description: A-share equity research with iFinD MCP — company deep dives, financial analysis, industry research, shareholder analysis, and research report discovery. Use when researching Chinese A-share companies, writing company analysis, building financial snapshots, or doing industry/sector research for Chinese stocks.
---

# A-Share Equity Research

Comprehensive A-share equity research workflow using iFinD MCP tools. Covers company fundamentals, financial analysis, shareholder structure, industry research, and report discovery.

## iFinD MCP Quick Reference

iFinD provides 7 MCP services. Primary use is `hexin-ifind-ds-stock-mcp`. Full reference: `references/ifind-mcp-guide.md`.

**Key tools (stock MCP):**

| Tool | Use Case | Example |
|---|---|---|
| `search_stocks` | Filter by criteria | "2026年上市的半导体公司" |
| `get_stock_summary` | Quick overview | "688789.SH的主营业务和行业" |
| `get_stock_financials` | Financial data | "688789.SH 近三年营收利润毛利率ROE" |
| `get_stock_shareholders` | Shareholder data | "688789.SH 2026Q1前十大股东" |
| `get_stock_performance` | Price/technical | "688789.SH最近一年最高价最低价" |
| `get_stock_info` | Basic info | "688789.SH的上市日期实际控制人" |
| `get_stock_events` | IPO, M&A events | "688789.SH的并购重组对外投资" |

**Known limitations:**
- No management bios/resumes
- No subsidiary lists (参控股公司 → use iFinD desktop F9)
- No dedicated research-report tool — but `search_news` (news MCP) returns 券商研报观点片段（研报观点以财经资讯形式传播），港股/美股公司同样有效
- No industry market size data
- fund/edb/bond/index MCPs untested
- 北交所 stocks: sparser data (no 申万 classification, incomplete product breakdowns)

**Query tips:**
- Always include stock code in queries — "688789.SH的2025年营收"
- For historical data, specify years: "2023年 2024年 2025年"
- Stock name must match iFinD's registered name (宏华数科 ≠ 宏华数码)
- Financial queries return latest period by default — add year for specific periods

**Critical parsing patterns:**

1. **Double JSON wrapping in `get_stock_financials`**: The response format is `content[0].text`, which itself is a JSON string. Parse it as:
   ```python
   inner = json.loads(content[0]['text'])
   if 'data' in inner:
       da = inner['data']
       if isinstance(da, str):
           da2 = json.loads(da)
           if 'answer' in da2: actual_text = da2['answer']
       elif isinstance(da, dict) and 'answer' in da: actual_text = da['answer']
   ```

2. **`get_stock_financials` requires stock CODES, not names**: Querying `"东方材料 三佳科技 总市值"` returns empty. Must use `"603110.SH 600520.SH 总市值"`. The regex to extract data: `\|\s*(\d{6}\.\w+)\s*\|\s*(.+?)\s*\|\s*(\d+\.?\d*)亿\s*\|`

3. **Batch size limit**: `get_stock_financials` handles ~8-10 stocks per call. Exceeding causes empty returns.

4. **`search_stocks` pool is limited**: Combining multiple conditions (市值+跌幅+行业) often returns too few results. Workaround: search by one dimension at a time (theme/concept only), then post-filter with `get_stock_financials` for market cap verification.

5. **HTTP direct calling pattern** (when MCP tools not loaded in session):
   ```python
   AUTH = <token from config.yaml>
   url = 'https://iFinD-MCP-endpoint'
   data = json.dumps({"jsonrpc":"2.0","id":1,"method":"tools/call",
       "params":{"name":"get_stock_financials","arguments":{"query":"..."}}}).encode()
   req = urllib.request.Request(url, data=data,
       headers={'Content-Type':'application/json','Authorization':AUTH})
   resp = json.loads(urllib.request.urlopen(req, timeout=120).read())
   ```

## Research Report Discovery

iFinD MCP 没有专门的研报数据库工具，但 **`search_news`（news MCP 的资讯片段检索）能搜到券商研报观点摘要**——研报观点以财经资讯/公众号/券商点评形式传播（如「东吴证券点评绿茶集团」「国金证券餐饮行业深度」）。查询用自然语言 + `time_start`/`time_end` + `size`（上限 20），港股/美股公司同样有效。

```python
tool_call('mcp__hexin_ifind_ds_news_mcp__search_news', {
  'query': '餐饮 券商研报 拓店 单店投资回收期',
  'time_start': '2025-09-01', 'time_end': '2026-09-30', 'size': 15
})
```

When iFinD MCP can't find reports:
- 东方财富研报平台: `data.eastmoney.com/report/` (accessible from Hermes terminal)
- 搜狗搜索 (sogou.com) and 360搜索 (so.com) work when Google/Bing blocked
- iFinD desktop: 研报平台 → keyword search

## Format Preferences

The user prefers concise, data-driven analysis. Key rules:

- **原文截图 vs AI 总结（交付形式）**：当用户要求把研报/研究材料"做成 PDF/文档"时，先确认要"AI 提炼总结"还是"原文截图"。用户对研报材料明确偏好**原文截图**（原始页面，不要 AI 提炼）——AI 总结版会被退回重做。做法：直接给原文截图（agent-browser 整页截图 + 切分 + 中文 PDF，见 references/web-tools-backup.md），或动手前先问一句"要原文还是总结"。

- **No cross-company comparisons** unless user explicitly asks. Never use another stock (especially 宏华数科) as a reference point in research write-ups.
- **Paragraph length**: Keep every section paragraph to 3-5 sentences maximum. Match the user's template length exactly — if their reference is 3 lines, yours should be 3 lines. Err on the side of shorter.
- **Report section templates** — output in plain text (not markdown tables unless user explicitly requests a table) for direct copy-paste:
  - 历史沿革: Chronological + M&A detail (标的/方式/目的/结果), plain text narrative
  - 股权情况: 控制权→总股本→解禁 three-paragraph structure
  - 高管持股: Table with 姓名/职务/持股数/占总股本/披露口径, then per-person bios with 【职务】header
  - 主营业务构成: Product-revenue-margin table (requested by user) + per-product paragraph descriptions
  - 结构演变特征 (3. 结构演变特征): Per-product paragraphs: "产品：2023–2025年营收由X增至Y…毛利率由A变为B…始终是/担当…"
  - 毛利率与净利率变化: 毛利率趋势→净利率趋势→核心矛盾, three tight sub-sections
  - 境内外收入 (4. 境内外收入结构): "核心特征：…" opening + 2-3 data sentences + short assessment
  - 近年营收趋势 (5. 近年营收趋势): 3-line summary: peak→decline→plateau, one-line assessment
  - 期间费用 (6.): 1-2 sentences listing ratios + 1 sentence assessment
  - ROE/ROA (7.): 2-3 sentences: trajectory + reason + assessment
  - 员工构成 (5.1): 1 sentence headcount + 1 sentence structure comment
  - 研发投入 (5.2): 1 sentence listing amounts/ratios + 1 sentence trend comment
  - 现金流 (5.3): 2 sentences: operating trend + investing trend + financing trend
  - 对外投资 (八.): Chronological subsidiary list + one-paragraph summary
- **Always include iFinD consensus estimates** (FY1/FY2/FY3) when available; label "—" when no coverage
- Full section format reference: `references/report-section-templates.md`

## PDF Extraction

For PPT-generated PDFs (common for research reports), install and use pymupdf:
```bash
pip install pymupdf
python -c "import fitz; doc=fitz.open('file.pdf'); [print(p.get_text()) for p in doc]"
```

### Image-only documents (PPT screenshot DOCX / scanned images)

融资 PPT/BP 转成的 DOCX 常是**纯图片**（每页 PPT 截图成一张图），`read_file` 报 "DOCX contains no extractable text"、`python-docx` 也提取不到。方案：`unzip -o file.docx -d /tmp/doc` 看 `word/media/*.png`，再用 **macOS Vision framework OCR**（中文质量好于 tesseract）：

```bash
pip install pyobjc-framework-Vision pyobjc-framework-Quartz
```

```python
import Vision, Quartz
from Foundation import NSURL
def ocr(path):
    src = Quartz.CGImageSourceCreateWithURL(NSURL.fileURLWithPath_(path), None)
    cg = Quartz.CGImageSourceCreateImageAtIndex(src, 0, None)
    req = Vision.VNRecognizeTextRequest.alloc().init()
    req.setRecognitionLevel_(Vision.VNRequestTextRecognitionLevelAccurate)
    req.setRecognitionLanguages_(["zh-Hans", "zh-Hant", "en-US"])
    Vision.VNImageRequestHandler.alloc().initWithCGImage_options_(cg, None).performRequests_error_([req], None)
    return [(o.boundingBox(), o.topCandidates_(1)[0].string()) for o in (req.results() or [])]
```

按 boundingBox 的 y 降序（上→下）、x 升序（左→右）排序还原阅读顺序。**坑**：图表柱状图的数值标签常 OCR 不到，只能拿到坐标轴刻度，具体柱高要估算或让用户确认。

## Valuation Comparison (PS 倍数)

估值对比 / 一级投资尽调：PE 失真（>100 倍或亏损）时改用 **PS（市销率）** 对比。

- 查市值/PE：`stock_highfreq_quotes`（data_mode=real_time，indicators="最新价,总市值,市盈率TTM"，symbols 逗号分隔 ≤10 只）
- 查收入：`get_stock_financials`（query 带代码 + "营业总收入"）
- PS = 总市值 / 营业总收入

Pre-IPO 未上市标的：对标上市公司 PS 后 **打 5-7 折**（一级流动性折价）。**下行保护锚**：用低于所有对标的保守倍数作退出估值算买入回报，不赌 IPO 高估值。

结论要"相对 vs 绝对"分开说：相对不贵（低于对标）≠ 绝对便宜（本身隐含高增长预期），不能混为一谈。

## Revenue Modeling

When the user asks to model revenue, forecast sales, or build operating models for Chinese-listed companies, load the full methodology from `references/revenue-modeling.md`. Key highlights:

- **Source hierarchy**: IPO prospectus → annual reports → comparables → industry reports → estimation (labeled)
- **Post-IPO disclosure degradation**: Many A-share companies drop volume/price disclosure after listing
- **Modeling sequence**: Extract actuals from prospectus → cross-verify with iFinD → search post-IPO reports → extrapolate with labeled assumptions
- **Excel structure**: Per-product sheets with color-coded provenance (green=actual, orange=estimated, red=forecast), plus a 总量校验 cross-validation sheet
- **CVD / new product lines**: Separate sheet, model as equipment × output × utilization × (1 - defect rate)

Worked example: `references/huifeng-diamond-prospectus.md` (惠丰钻石 920725.BJ).

## Related Skills

- `equity-research`: IBES consensus-based Western equity research

## Web Tools & Integrations

- `references/web-tools-backup.md` — Firecrawl CLI + agent-browser fallback when `web_search`/`web_extract` unavailable
- `references/notion-api.md` — Notion API: search pages + append blocks via curl, batch size limits

## Format Templates & References

- `references/report-section-templates.md` — Exact per-section format templates (3-5 sentences each) for: 结构演变特征, 毛利率与净利率变化, 境内外收入, 近年营收趋势, 期间费用, ROE/ROA, 员工构成, 研发投入, 现金流, 对外投资
- `references/stock-memo-format.md` — Compact research memo format for quick company analysis
- `references/stock-screening-excel.md` — Stock screening Excel template
- `references/management-profile-template.md` — Executive profile & shareholding format
- `references/workpaper-template.md` — 行研底稿模板
- `references/revenue-modeling.md` — Revenue modeling methodology
- `references/huifeng-diamond-prospectus.md` — Worked example: 惠丰钻石
- `references/ifind-mcp-guide.md` — iFinD MCP tool reference
