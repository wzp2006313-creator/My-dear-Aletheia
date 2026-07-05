---
name: a-share-revenue-modeling
description: >
  Build revenue forecasting models for A-share companies, especially when post-IPO
  disclosure is thinner than prospectus data. Use when the user asks to model revenue,
  forecast sales, or build operating models for Chinese-listed companies.
---

# A-Share Revenue Modeling

## Source Hierarchy (mandatory — follow this order)

1. **招股说明书（IPO Prospectus）** — the single best source. Almost always includes volume (销量) × price (单价) by product segment, plus产能/产量/销量 tables. Search with `iFinD search_notice` or manual retrieval.
2. **年报（Annual Reports）** — post-IPO, many A-share companies STOP disclosing volume/price by segment. They only disclose revenue/cost/gross margin. Check EVERY annual report with `search_notice` before concluding data doesn't exist.
3. **可比公司（Comparables）** — check their prospectuses and annual report 问询函回复 for the same product category. Use as ceiling/floor benchmarks, not direct substitution.
4. **行业报告（Industry Reports）** — CPIA, 行业协会,券商研报. Use for market-level pricing trends, not company-specific assumptions.
5. **推算（Estimation）** — only after exhausting 1-4. Must be labeled as "推算值" and cross-validated against total production constraints.

## Key Pitfall

**Post-IPO disclosure degradation.** Many A-share companies (especially on 北交所/创业板) disclose full volume × price in the prospectus, then drop both from annual reports after listing. Annual reports keep only revenue / cost / gross margin by segment. DO NOT assume the data isn't there without checking every year's report — but also DO NOT assume it IS there without verifying. The phrase "销售量增长" in an annual report is a qualitative signal, not a number.

## Modeling Sequence

1. Extract **actual** historical volume & price from prospectus (usually 3 years: T-3, T-2, T-1)
2. Cross-verify: prospectus price × volume ≈ iFinD revenue (should match within 1%)
3. For post-IPO years: search annual reports for volume/price disclosures
4. If missing: use **毛利率 trend** as price direction signal (margin ↓ = price pressure), **annual report qualitative statements** as volume direction signal ("销售量增长"), and **comparable company pricing** as upper/lower bounds
5. Anchor the last known actual data point, then extrapolate with clear assumptions
6. **Cross-validate**: sum of segment volumes ≤ total production capacity (if known)
7. Label every estimate as "推算值" with source justification in a visible column

## Price Assumption Rules

- NEVER guess a price without citing a source
- Historical actuals from prospectus are the only hard anchors
- For forward estimates: cite specific annual report language, comparable data, or industry reports
- If using industry averages, state the source and conversion (e.g. "3909.6元/吨 from 行业报告 → 0.078元/克拉" — and verify the conversion makes sense)
- Price trends must be consistent with margin trends (declining margin → declining price)

## Volume Assumption Rules

- Volume = Revenue ÷ Price (derived, not independent)
- Must sum to ≤ total production capacity × utilization rate
- Utilization rate must be plausible (30-90% range; explain outliers)
- If two products' estimated volumes exceed total production, the price assumptions are WRONG — fix prices, not volumes

## Excel Structure

Per product sheet: Year | Revenue | Revenue YoY | Gross Margin | Price | Price YoY | Volume | Volume YoY | Source

Color coding:
- Green: 招股书 actual ✓
- Orange: 推算值 (estimation)
- Red: 预测值 (forecast)

Add a separate sheet for 总量校验 (cross-validation): Year | Product A Vol | Product B Vol | Other | Total | Capacity | Utilization

## CVD / New Product Lines

When the company is investing in a new product category (e.g. CVD diamond materials via MPCVD):
- Create a SEPARATE sheet for the new line — do NOT bury it in "其他收入"
- Model as: Equipment count × monthly output per unit × utilization × (1 - defect rate) → output volume
- Price by sub-product (e.g. copper-diamond composite vs. pure CVD heat spreader — very different ASP)
- Note the cost structure difference: CVD is depreciation-heavy, traditional abrasive is raw-material-heavy

## iFinD MCP Usage

- `get_stock_financials` with query describing entity + indicators + date → returns revenue/cost/margin by segment
- `search_notice` with query for prospectus/annual report text → returns relevant snippets
- Prospectus search should include "销量" "单价" "元/克拉" to catch volume/price tables

## Reference Case

See `references/huifeng-diamond-prospectus.md` for a worked example: prospectus extraction, cross-verification with iFinD, comparable benchmarking (力量钻石), and post-IPO disclosure gap handling for 惠丰钻石 (920725.BJ).
