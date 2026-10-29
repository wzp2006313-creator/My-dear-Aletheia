# iFinD MCP Usage Guide

Full reference for using iFinD MCP tools for A-share equity research. All MCP servers use streamablehttp transport on port 8643.

## Available MCP Servers

| Server | Status | Description |
|---|---|---|
| hexin-ifind-ds-stock-mcp | ✅ Active | Stock data (primary use) |
| hexin-ifind-ds-fund-mcp | ⚠️ Untested | Fund data |
| hexin-ifind-ds-edb-mcp | ⚠️ Untested | Economic database |
| hexin-ifind-ds-news-mcp | ❌ Broken (400) | News |
| hexin-ifind-ds-bond-mcp | ⚠️ Untested | Bond data |
| hexin-ifind-ds-global-stock-mcp | ⚠️ Untested | Global stocks |
| hexin-ifind-ds-index-mcp | ⚠️ Untested | Index data |

## Stock MCP Tool Reference

### get_stock_summary
Quick overview — best first tool for any new stock.
```
"688789.SH的主营业务和所属行业"
"688789.SH的控股股东、实际控制人"
```
Returns: company info, financial summary, shareholder summary, IPO info.
Limitation: may not return structured tables for 北交所 stocks.

### get_stock_financials
The most versatile financial data tool.
```
"688789.SH 近五年营业收入、归母净利润、毛利率、ROE"
"688789.SH 近三年销售费用率、管理费用率、研发费用率"
"688789.SH 经营性现金流净额、投资性现金流净额"
```
Always include a year or period. Default returns latest quarter only.
For regional data: "688789.SH的境内收入、境外收入、境内毛利率、境外毛利率"

### get_stock_shareholders
Shareholder structure data.
```
"688789.SH 2026年一季报前十大股东"
"688789.SH的股本结构、限售股"
```
Returns: top 10 shareholders, share counts, percentages, shareholder types.
Does NOT return: management shareholdings (高管持股), subsidiary lists.

### get_stock_info
Basic company information.
```
"688789.SH的成立日期、上市日期、注册资本"
"688789.SH的实际控制人"
```
Returns: listing date, incorporation date, registered capital, legal representative, actual controller.

### get_stock_performance
Price and technical data.
```
"688789.SH最近一年的最高价和最低价"
```
Returns: OHLC, P/E, volume, technical indicators.

### get_stock_events
IPO, M&A, and corporate events.
```
"688789.SH的IPO信息、发行价格、募集资金"
"688789.SH上市以来的并购重组"
```
Returns: event type, dates, transaction targets (names only, no amounts).
Does NOT return: transaction amounts, detailed deal terms.

### search_stocks
Find stocks by criteria (natural language).
```
"2026年上市的半导体公司"
"做数码印花的A股上市公司"
"PCB油墨相关上市公司"
```
Returns: stock codes, names, IPO dates if applicable.
Limitation: may return empty for niche or poorly-described categories.

## What iFinD MCP CANNOT Do

- Management bios/resumes (use 招股书 or 年报 directly)
- Subsidiary/affiliate lists (use iFinD desktop F9 → 参控股公司)
- Industry research reports (use iFinD desktop 研报平台 or eastmoney.com)
- Industry market size or penetration data
- Detailed M&A transaction amounts (start-end dates only)
- Employee count breakdown by function (sometimes available in financials)
- Real-time news feeds (news MCP broken)

## Query Best Practices

1. **Always include stock code**: "688789.SH的2025年营收" not "宏华数科的2025年营收"
2. **Specify exact years**: Without year, defaults to latest reporting period
3. **Use registered names**: 宏华数科 (not 宏华数码), 容大感光 (300576, check code)
4. **Batch queries sparingly**: Large batch queries may hit rate limits
5. **Financial ratios**: Combine multiple metrics in one query for efficiency
6. **Region data**: Include 境内/境外 for geographic split

## MCP Connection Setup

MCP requires the `mcp` Python package installed in Hermes venv:
```bash
# If MCP tools not showing up:
/Users/eason/.hermes/hermes-agent/venv/bin/python -m ensurepip --default-pip
/Users/eason/.hermes/hermes-agent/venv/bin/python -m pip install mcp
# Then /reset in chat to reload tools
```

## Research Report Alternative Sources

When iFinD MCP fails to find reports, try these (accessible from Hermes terminal):
- **东方财富**: `data.eastmoney.com/report/zygdb/stock/<CODE>.html` — returns JSON with report data
- **搜狗搜索**: `sogou.com/web?query=...` — renders results in HTML (no JS required)
- **360搜索**: `so.com/s?q=...` — renders results in HTML (no JS required)
- **Google/Bing/Baidu**: Often blocked from this environment

For PPT-generated PDFs (common format for sell-side reports):
```bash
pip install pymupdf
python -c "import fitz; doc=fitz.open('file.pdf'); [print(p.get_text()) for p in doc]"
```
