---
name: fund-portfolio-monitor
description: Daily fund portfolio monitoring — fetch real-time NAV estimates for 展鹏's 17-fund portfolio via 天天基金 API, generate structured daily reports with loss alerts and strategy notes. Triggers on "基金快报", "基金监控", "每日基金", "展鹏的基金", "基金管家", "fund portfolio", "fund monitor", or cron-scheduled fund check tasks.
---

# Fund Portfolio Monitor

Daily cron task: fetch real-time net asset value (NAV) estimates for 展鹏's portfolio, generate a structured daily report with loss warnings and strategy suggestions.

## Portfolio Overview

17 funds, ~¥385K total market value, ~¥57K cumulative profit. See `references/portfolio.md` for the complete fund list with codes and cost basis.

## Workflow

### Step 1: Fetch NAV data

Choose the first available data source from this priority chain:

**OPTION 1 — iFinD Fund MCP** (most reliable when MCP servers are up):

Use `mcp__hexin_ifind_ds_fund_mcp__get_fund_market_performance` with SINGLE fund queries:

```json
{"query": "华安黄金ETF联接C(000217)最近一个交易日的单位净值和涨跌幅"}
```

Key fields returned: `单位净值`, `单位净值增长率` (daily change %), `净值日期`.

⚠️ **CRITICAL**: Query ONE fund at a time. Batch queries (multiple fund codes in one `query`) return empty results. This means 10+ separate tool calls per report. Budget ~30 seconds for a full portfolio fetch.

The iFinD data includes confirmed NAV (not estimated) and is the highest-quality source. Use it whenever the MCP servers are connected.

**OPTION 2 — 天天基金 estimated NAV API** (try when MCP is down):

```bash
curl -s "https://fundgz.1234567.com.cn/js/{code}.js"
```

Returns JSONP with `dwjz` (NAV), `gsz` (estimated NAV), `gszzl` (estimated change %), `gztime`.

**OPTION 3 — Sina Finance API** (fallback when fundgz returns 404 or is blocked):

```bash
curl -s "https://hq.sinajs.cn/list=f_{code}" -H "Referer: https://finance.sina.com.cn"
```

Returns: `var hq_str_f_{code}="名称,最新净值,昨收,累计净值,日期,..."`

The Sina API returns yesterday's NAV only (no intraday estimate), but is extremely reliable. Fields are comma-separated; Chinese names appear as GBK-encoded (garbled), but the numeric data is clean.

Fetch all funds in one request:
```bash
codes="f_000217,f_012734,f_016708,f_002207,f_022364,f_014855,f_020671,f_012349,f_022365,f_018301"
curl -s "https://hq.sinajs.cn/list=${codes}" -H "Referer: https://finance.sina.com.cn"
```

See `references/sina-api-guide.md` for the full Sina API reference including fund, index, and commodity codes.

### Step 1.5: Find missing/incorrect fund codes

If a fund code from the portfolio returns wrong data or empty result, search for the correct code:

```bash
# Search API — set callback to empty string for raw JSON (no JSONP wrapper needed)
curl -s "https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?callback=&search=suggest&m=1&key={keyword}"
```

Parse with: `python3 -c "import sys,json; d=json.load(sys.stdin); ..."` (direct JSON parse, no callback regex needed).

The `FundBaseInfo` object in `Datas[0]` contains: `FCODE`, `SHORTNAME`, `DWJZ` (latest NAV), `FSRQ` (NAV date), `FTYPE`.

**Pro tip**: If a full name returns empty results, try shorter, more distinctive keywords (e.g., "科创芯片" instead of "易方达科创板芯片ETF联接C", "永赢科技智选" instead of "永赢科技智选混合A").

### Quick Reference

- `references/portfolio.md` — complete portfolio with all fund codes
- `references/sina-api-guide.md` — Sina API code catalog: indices, commodities, sector-to-fund mappings
- `references/report-template.md` — report structure and strategy framework

### Step 2: Get market context

**PRIMARY — Sina Finance API** (most reliable for indices):

```bash
# Major A-share indices (上证, 深证, 创业板, 科创50, 沪深300)
curl -s "https://hq.sinajs.cn/list=s_sh000001,s_sz399001,s_sz399006,s_sh000688,s_sh000300" \
  -H "Referer: https://finance.sina.com.cn"

# HK indices (恒生, 恒生科技)
curl -s "https://hq.sinajs.cn/list=rt_hkHSI,rt_hkHSTECH" \
  -H "Referer: https://finance.sina.com.cn"

# Commodity (伦敦金, 纽约原油)
curl -s "https://hq.sinajs.cn/list=hf_XAU,hf_CL" \
  -H "Referer: https://finance.sina.com.cn"

# Sector indices: 有色金属(sh000819), 科创芯片(sh000685), CSSW电子(sz399811), 中证有色(sz399395)
curl -s "https://hq.sinajs.cn/list=sh000819,sh000685,sz399811,sz399395" \
  -H "Referer: https://finance.sina.com.cn"
```

Returns format: `var hq_str_{code}="名称,当前价,昨收价,开盘价,最高价,最低价,...";`

**FALLBACK — eastmoney push2 API**:

```bash
curl -s "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=1.000001,100.HSI,100.HSTECH&fields=f2,f3,f4,f12,f14" \
  -H "Referer: https://quote.eastmoney.com/"
```

See `references/sina-api-guide.md` for the full index code catalog.

### Step 2.5: Get 5-day historical NAV for trend analysis (OPTIONAL)

```bash
# Try eastmoney f10 API first
curl -s "https://api.fund.eastmoney.com/f10/lsjz?callback=cb&fundCode={code}&pageIndex=1&pageSize=5" \
  -H "Referer: https://fundf10.eastmoney.com/"
```

Returns: `FSRQ` (date), `DWJZ` (NAV), `JZZZL` (daily change%). 

**Note**: The eastmoney f10 API has become increasingly unreliable (often returns 404/ErrCode=4). When it fails, skip the 5-day trend and rely on today's sector index movements to infer short-term direction. The Sina API only provides the single latest NAV, so multi-day trend analysis requires the f10 API or MCP tools.

### Step 3: Calculate key metrics

For each losing fund, compute:
- **回本需涨** = abs(亏损金额) / 当前市值 × 100%
- **亏损率** from portfolio table

### Step 4: Generate report

Follow the established report format (see `references/report-template.md`):

1. **Header**: 📊 展鹏基金快报 | 日期 + 市场概览（上证/恒生/板块ETF表现）
2. **🔴 亏损关注**: Detailed table + 5-day trend + analysis for the 3 losing funds
3. **🟢 盈利持仓**: Today's top/bottom 3 movers + full valuation list
4. **💡 今日策略**: 4 sections (有色/金银珠宝, 恒生科技, 科技止盈, 其他QDII)
5. **📊 组合健康度总评**: Optional — include when MCP/news sources available, skip in lean/cron mode
6. **⚠️ 免责声明**: Always include disclaimer, note AI-analysis nature

### Step 5: Strategy Framework

Apply consistent strategy logic:
- **前海开源金银珠宝 (-27%)**: Do NOT add position. Wait for gold to stabilize above $4,200. 31% recovery needed.
- **华夏有色金属 (-13.7%)**: Watch for oversold bounce but trend not reversed. No averaging down.
- **天弘恒生科技 (-7.8%)**: Lightest loss, easiest to recover. Monitor HK tech index for bounce signals.
- **科技止盈 (AI/半导体/芯片)**: Positions at +44%~+81% profit. Recommend partial profit-taking when cumulative gain exceeds 100%, or set trailing stop at 15% from peak.
- **华安黄金 (+4.7%)**: Hold as portfolio stabilizer. Don't add during gold downtrend.

## Pitfalls

- **iFinD Fund MCP: single-query ONLY** — `get_fund_market_performance` returns empty results for batch queries. Must query one fund per call. Budget ~30s for a full portfolio fetch. When in a hurry, fall back to Sina API for bulk queries.
- **iFinD MCP servers may be disconnected** (hexin-ifind-ds-*) — the fund, index, news servers can go down (token expiry, gateway issues). When the fund MCP is down, fall back to Sina API for NAV data. When all MCP servers are down, Sina API + eastmoney fund search API are sufficient to build a complete report.
- **fundgz.1234567.com.cn API has become unreliable** — as of July 2026, it frequently returns 404 for ALL fund codes. When this happens, skip to the Sina API.
- **eastmoney f10 API may return 404/ErrCode=4** — the historical NAV endpoint at `api.fund.eastmoney.com/f10/lsjz` is also increasingly flaky. 
- **eastmoney fundf10 pages are blocked** by web_extract. Don't bother trying them.
- **web_search may be unavailable in cron** (requires FIRECRAWL_API_KEY which may not be configured in cron profiles). Don't rely on it for fund data — use iFinD MCP or Sina API instead.
- **execute_code is blocked in cron mode** — use individual tool calls for MCP queries or terminal `curl` calls. Multi-fund queries in Sina format can be combined into single `curl` calls with comma-separated codes.
- **QDII funds** (天弘恒生科技, 华安纳斯达克) have 1-2 day NAV lag. Note this in the report. The QDII code field `净值日期` in iFinD may show T-1 or T-2 relative to A-share funds.
- **Sina sector-index field order (CRITICAL, corrected 08-20)**: the sh/sz sector index endpoints (sh000819, sh000685, sz399811, sz399970, sz399395) return `名称,开盘价,昨收价,收盘价(最新),最高价,最低价` — NOT `名称,当前价,昨收,开盘,最高,最低` as older docs claimed. The FIRST numeric field is the **open price**, not the current price. To compute 涨跌幅 use `(字段3收盘 − 字段2昨收) / 字段2昨收`. Cross-checked against eastmoney push2: Sina 9222.50(开盘)/8990.40(昨收)/9090.37(收盘) == eastmoney 今开9222.50/昨收8990.40/最新9090.37, 涨跌+1.11%. The broad `s_` index endpoint (s_sh000001) is different and DOES return 涨跌幅 directly in field3. See `references/sina-api-guide.md`.
- **Sina fund-NAV field order** is actually `名称,单位净值,累计净值,昨收(前日净值),净值日期,规模/份额` — NOT `名称,最新净值,昨收,累计净值,日期` as some docs say. The two NAV fields (单位/累计) are equal for C-class funds (no cash dividends), and 昨收 is the 4th field. Daily change = (单位净值 − 昨收) / 昨收. Verify: 华安黄金 000217 → 单位 3.1657, 昨收 3.1965, −0.96% on 08-14.
- **macOS `grep -P` (Perl regex) is NOT available** — the default BSD grep on macOS lacks `-P`. Use `python3 -c` for regex parsing or pipe through `sed` instead.
- **Sina API returns GBK encoding** — Chinese fund/index names will appear garbled. Use the fund codes (which are clean) for identification. The numeric fields (NAV, prices, dates) are all ASCII-safe.
- **Some fund names are hard to search** — the eastmoney fund search API (`fundsuggest.eastmoney.com`) may return empty results for long fund names. Try shorter, more distinctive keywords (e.g., "科创芯片" instead of "易方达科创板芯片ETF联接C").
- **Fund codes can be misremembered** — always consult `references/portfolio.md` for the authoritative code list. Common mistakes: 华夏有色金属 is 016708 (not 012513), 易方达科创芯片 is 020671 (not 017648), 永赢科技智选 is 022364/022365 (发起式 suffix, not 008920/008921).
