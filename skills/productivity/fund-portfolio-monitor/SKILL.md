---
name: fund-portfolio-monitor
description: Daily fund portfolio monitoring — fetch real-time NAV estimates for 展鹏's 17-fund portfolio via 天天基金 API, generate structured daily reports with loss alerts and strategy notes. Triggers on "基金快报", "基金监控", "每日基金", "展鹏的基金", "基金管家", "fund portfolio", "fund monitor", or cron-scheduled fund check tasks.
---

# Fund Portfolio Monitor

Daily cron task: fetch real-time net asset value (NAV) estimates for 展鹏's portfolio, generate a structured daily report with loss warnings and strategy suggestions.

## Portfolio Overview

17 funds, ~¥385K total market value, ~¥57K cumulative profit. See `references/portfolio.md` for the complete fund list with codes and cost basis.

## Workflow

### Step 1: Fetch NAV data via 天天基金 API

**DO NOT use web_search, web_extract, or browser tools for fund NAV data.** These are either blocked (eastmoney fundf10, danjuanfunds) or too slow. Use the direct API:

```bash
curl -s "https://fundgz.1234567.com.cn/js/{code}.js"
```

**Note**: Both HTTP and HTTPS work, but HTTPS is preferred. The API has no auth requirements.

Returns JSONP in the format:
```json
{
  "fundcode": "002207",
  "name": "前海开源金银珠宝混合C",
  "jzrq": "2026-06-29",
  "dwjz": "2.2930",
  "gsz": "2.2671",
  "gszzl": "-1.13",
  "gztime": "2026-06-30 14:28"
}
```

**Fields:**
- `jzrq`: NAV date (last published)
- `dwjz`: unit NAV (单位净值)
- `gsz`: estimated NAV (估算值)
- `gszzl`: estimated change % (估算涨跌幅)
- `gztime`: estimate timestamp

Fetch all funds in one loop:
```bash
for code in 002207 016708 012349 000217 012734 022364 014855 020671 022365 018301 006479 002697; do
  echo "=== $code ==="
  curl -s "https://fundgz.1234567.com.cn/js/${code}.js"
  echo ""
done
```

### Step 1.5: Find missing/incorrect fund codes

If a fund code from the portfolio returns wrong data or empty result, search for the correct code:

```bash
# Search API - returns JSON with fund codes, names, and latest NAV
curl -s "https://fundsuggest.eastmoney.com/FundSearch/api/FundSearchAPI.ashx?callback=cb&m=9&key={keyword}"
```

Parse with: `python3 -c "import sys,json,re; m=re.search(r'cb\((.+)\)', sys.stdin.read(), re.DOTALL); ..."`

The `FundBaseInfo` object contains: `FCODE`, `SHORTNAME`, `DWJZ` (latest NAV), `FSRQ` (NAV date).

**Pro tip**: If a full name returns empty results, try shorter keywords (e.g., "科创芯片" instead of "易方达科创板芯片ETF联接").

### Step 2: Get market context via eastmoney push API

**Prefer the push API over web_search** — it's faster and more reliable:

```bash
# Get major indices (上证, 恒生, 恒生科技)
curl -s "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=1.000001,100.HSI,100.HSTECH&fields=f2,f3,f4,f12,f14" \
  -H "Referer: https://quote.eastmoney.com/"

# Get sector ETFs (黄金, 半导体, 有色, 科创50)
curl -s "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&secids=1.518880,1.512480,1.512400,1.588000&fields=f2,f3,f14" \
  -H "Referer: https://quote.eastmoney.com/"
```

Fields: `f2`=price, `f3`=change%, `f4`=change, `f12`=code, `f14`=name.

### Step 2.5: Get 5-day historical NAV for trend analysis

```bash
curl -s "https://api.fund.eastmoney.com/f10/lsjz?callback=cb&fundCode={code}&pageIndex=1&pageSize=5" \
  -H "Referer: https://fundf10.eastmoney.com/"
```

Returns: `FSRQ` (date), `DWJZ` (NAV), `JZZZL` (daily change%). Use at least for the 3 losing funds.

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

- **eastmoney fundf10 pages are blocked** by web_extract. Don't bother trying them.
- **danjuanfunds.com is blocked** by web_extract and uses heavy JS rendering — browser navigation works but extracting NAV is slow.
- **execute_code is blocked in cron mode** — use terminal curl instead.
- **QDII funds** (天弘恒生科技, 广发纳斯达克) have 1-2 day NAV lag. Note this in the report.
- The API uses **HTTP** (not HTTPS) — this is normal for this endpoint. The plain HTTP warning from the security scanner is expected.
- **Some funds may have different codes than their names suggest**. Always verify via the API response's `name` field.
- **macOS `grep -P` (Perl regex) is NOT available** — the default BSD grep on macOS lacks `-P`. Use `python3 -c` for regex parsing or pipe through `sed` instead.
- **MCP servers may be disconnected** (hexin-ifind-ds-*). The fund and news MCP servers are optional. When they're down, fall back to the direct eastmoney APIs described above — they all work without authentication.
