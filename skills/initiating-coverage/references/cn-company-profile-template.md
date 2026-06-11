# 中国上市公司简析模板 (Company Profile Template)

When writing a lightweight Chinese A-share company profile (not a full initiation report), follow this structure and style. Modeled after institutional 四方达 analysis format.

## Format Rules

1. **Concise, one-line-per-item**: Each product/segment/trend gets a single dense paragraph. No multi-paragraph expansions for a single data point.
2. **Data-first**: Lead every section with specific numbers (营收金额, 占比, 毛利率, 同比增速).
3. **对比锚定**: Always compare to the reference company (四方达) or industry peers in at least one dimension.
4. **No markdown-heavy formatting**: Use natural paragraph breaks with a single blank line, not ## headings within sections. Bold sparingly.

## Section Template

### 1. 业务定位与产品体系
One intro sentence defining the company. Then categorize products into 3-4 buckets with one-line descriptions each.

### 2. 产品收入与利润结构
Each product line gets ONE compact paragraph:
- Product name: 营收 (占比%), 同比增速, 毛利率, 利润额 + 利润占比% (if available), core judgment.

End with a structural trend summary comparing product mix shift over 3-5 years.

### 3. 地区收入结构
Core feature in one sentence. Then domestic vs overseas each in one paragraph. Conclude with overseas strategy evolution.

### 4. 近年营收趋势
Phase-based narrative (3-4 phases max) covering 2016-present. Each phase: year range → revenue range → CAGR or key driver.

### 5. 盈利能力分析 (费用率 + ROE/ROA)
Two sub-sections:
- 期间费用率: List current year ratios, note trends, one-line judgment.
- ROE/ROA趋势: Narrative of rise/fall with key inflection points explained.

## Data Sources

### P&L line items (费用, 利润)
Navigate to Sina Finance P&L pages:
```
http://money.finance.sina.com.cn/corp/go.php/vFD_ProfitStatement/stockid/688028/ctrl/YEAR/displaytype/4.phtml
```
Extract via `browser_console`:
```js
(()=>{const t=document.body.innerText;const i=t.indexOf('研发费用');return i>0?t.substring(i,i+80):'nf';})()
```
Annual (Q4 cumulative) is the first column after the label.

### Product-level revenue/cost/profit breakdown
同花顺 F10 经营分析 → 主营构成分析:
```
http://basic.10jqka.com.cn/STOCKCODE/operate.html
```
Use `browser_console` to extract from the table (table index 3 usually):
```js
document.querySelectorAll('table')[3] // has columns: 业务名称 | 营业收入 | 收入比例 | 营业成本 | 成本比例 | 主营利润 | 利润比例 | 毛利率
```

### ROE/ROA historical
Sina financial guide pages:
```
http://money.finance.sina.com.cn/corp/go.php/vFD_FinancialGuideLine/stockid/688028/ctrl/YEAR/displaytype/4.phtml
```
Extract 净资产收益率 and 加权净资产收益率 from the page text.

### Regional revenue
年报 section "主营业务分地区" in annual report or search for "国内" "国外" 收入 毛利率 in the annual report description.

## Data Sources (continued)

### Cash flow statement (经营性/投资性/筹资性现金流)
Navigate to Sina Finance CashFlow pages:
```
http://money.finance.sina.com.cn/corp/go.php/vFD_CashFlow/stockid/688028/ctrl/YEAR/displaytype/4.phtml
```
Extract all four key line items in one regex pass:
```js
(()=>{const t=document.body.innerText;const r=/经营活动产生的现金流量净额\s+([\d\-,.]+).*?投资活动产生的现金流量净额\s+([\d\-,.]+).*?筹资活动产生的现金流量净额\s+([\d\-,.]+).*?现金及现金等价物净增加额\s+([\d\-,.]+)/s;const m=t.match(r);return m?JSON.stringify({经营:m[1],投资:m[2],筹资:m[3],现金:m[4]}):'nf';})()
```
The first column is the full-year figure. To get 10 years of data, loop through years 2016-2025 in the URL, extract each, then compile into a table (convert 万元 → 亿元 by dividing by 10,000).

### iFinD Excel formula syntax
When the user asks about writing iFinD formulas for Excel:
```
=@thsiFinD("指标代码", 股票代码单元格, 年份单元格, 100)/100000000
```
- `"指标代码"`: unique code per financial metric (use iFinD's 公式向导 to search by Chinese name)
- `$B$1`: locked stock code cell (e.g. 688028)
- `Y4`: year cell reference
- `100`: report type (100=年报, 50=中报, 30=三季报, 10=一季报)
- `/100000000`: convert from 元 to 亿元
Common codes: ths_revenue (营收), ths_np_cg (归母净利润), ths_gross_margin (毛利率), ths_roe (ROE), ths_rd_expense (研发费用), etc.

## Pitfalls

- Do NOT write multi-paragraph product descriptions. The user prefers density. Each product or segment gets ONE compact paragraph.
- Do NOT estimate毛利率 without citing the source; if unsure, search specifically for the exact product毛利率 from the annual report.
- The 同花顺 page loads data dynamically — if the table shows "加载中...", click on the "利润比例" tab first, then extract.
- 四方达's template uses "资源开采/工程施工类" and "精密加工类" as product categories — adapt to the target company's actual products, don't force-fit.
- Do NOT force comparisons to 四方达 unless the user's template explicitly includes it. If the user says "不用管四方达", remove the comparison and keep the section self-contained.
- When the user asks to shorten a section ("简短一点", "是不是太长了"), compress to the minimum: remove explanatory bridging sentences, keep only data + one-line judgment per item.
- For multi-year data extraction from Sina, use the regex approach above rather than individual per-item extraction — it's faster and captures all four cash flow items in one shot.
