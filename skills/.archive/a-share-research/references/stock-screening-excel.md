# Stock Screening Excel Template

Use this format when generating stock screening / watchlist Excel files.

## Columns (standard 11-column layout)

| Col | Header | Width | Align | Notes |
|-----|--------|-------|-------|-------|
| A | 序号 | 5 | center | Sequential numbering |
| B | 股票名称 | 14 | center | Full Chinese name |
| C | 代码 | 9 | center | 6-digit code |
| D | 市值(亿) | 8 | center | Current market cap |
| E | 跌幅 | 8 | center | YTD decline % |
| F | 毛利率 | 7 | center | Latest fiscal year |
| G | 2025A净利 | 14 | center | 2025 actual, with YoY change |
| H | 2026E净利 | 9 | center | iFinD consensus FY1 |
| I | 2027E净利 | 14 | center | iFinD consensus FY2 |
| J | PE(26E) | 14 | center | Forward PE based on 2026E consensus |
| K | 推荐逻辑 | 50 | left | 1-2 sentence investment thesis |

## Optional columns
- Col L (hidden): Type label — 拐点确认 / 稳健增长 / 周期回暖 / 产能爆发 / 特斯拉期权 / 机器人期权 / 核聚变期权

## Styling

```
Header:      Font 微软雅黑 10pt bold white, Fill #2F5496 (dark blue), Center aligned
Body rows:   Font 微软雅黑 10pt, Alternating #D6E4F0 (light blue) / #FFFFFF (white)
Title row:   Font 微软雅黑 14pt bold, Fill #F5F5F5, Merged A-K
Footer:      Font 微软雅黑 8pt color #888888, Fill #F5F5F5
Borders:     Thin #CCCCCC on all cells
Type labels: Font 微软雅黑 9pt bold, Color #2F5496 for confirmed/growth, #E60000 for option-type
Row height:  Header 26px, Data 80-85px, Title 30-32px
```

## iFinD Consensus Integration

When available (惠柏/广信/中研 had consensus; 气派/禾川/凯立/国光 had none):
- Show "—" for blanks (no analyst coverage)
- Show 2026E forecast with FY1, 2027E with FY2
- Calculate forward PE based on current market cap ÷ consensus FY1
- For non-profitable stocks, show "扭亏中" or "—" instead of PE

## Footer

Two footer rows:
1. Data source note: "注：市值/跌幅基于YYYY.MM.DD数据；净利为202XA或202XE；PE标注'—'表示暂无。数据来源：iFinD。中泰证券研究所整理"
2. Portfolio summary: "组合特征：市值X-Y亿 | N只拐点/增长型 + N只期权型 | 剔除XX链"

## Example output
See previous run: `~/Desktop/小市值精选标的_最终版.xlsx`
