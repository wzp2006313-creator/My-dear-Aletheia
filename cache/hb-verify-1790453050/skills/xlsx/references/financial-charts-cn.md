# Chinese Financial Report Chart Building

## Color Scheme (用户偏好)

Standard scheme for Chinese financial / industry research reports:

| 用途 | 颜色 | 色值 |
|------|------|------|
| 主色（标题栏、主力图表系列） | 标准深红 | `#C00000` |
| 辅色（第二系列、折线叠加） | 标准红 | `#E60000` |
| 第三色（辅助系列） | 暗红 | `#990000` |

Apply via openpyxl:
```python
DEEP_RED = "C00000"
STANDARD_RED = "E60000"
AUX_RED = "990000"

HEADER_FILL = PatternFill(start_color=DEEP_RED, end_color=DEEP_RED, fill_type="solid")
HEADER_FONT = Font(name="微软雅黑", bold=True, color="FFFFFF", size=11)
ALT_FILL = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")
```

## Chart Types for Financial Reports

### 1. Bar + Line Combo (营收/资产负债 + 比率)
Use when showing absolute values (bar) alongside a ratio (line overlay):
```python
# Primary bar chart
chart = BarChart()
chart.y_axis.axId = 100
chart.y_axis.crossBetween = "between"

# Line overlay for ratio
line = LineChart()
line.y_axis.axId = 200
line.y_axis.crosses = "max"
line.series[0].graphicalProperties.line.dashStyle = "dash"

chart += line
```

### 2. Dual Line Chart (ROA/ROE, 毛利率/净利率)
```python
chart = LineChart()
chart.series[0].graphicalProperties.line.solidFill = DEEP_RED    # primary
chart.series[1].graphicalProperties.line.solidFill = STANDARD_RED  # secondary
chart.series[1].graphicalProperties.line.dashStyle = "dash"        # dashed for differentiation
chart.series[0].graphicalProperties.line.width = 28000             # ~2pt
```

### 3. Chart Sizing
```python
chart.width = 22   # cm
chart.height = 13  # cm (or 14 for taller)
chart.legend.position = 'b'  # bottom legend
```

## Common Pitfalls

### MergedCell Clearing
When rewriting sheet content, you MUST unmerge before clearing:
```python
# Correct order:
for m in list(ws.merged_cells.ranges):
    ws.unmerge_cells(str(m))
for row in range(1, ws.max_row + 1):
    for col in range(1, ws.max_column + 1):
        ws.cell(row=row, column=col).value = None
```

Setting `.value = None` on a MergedCell raises:
`AttributeError: 'MergedCell' object attribute 'value' is read-only`

### xlsb → xlsx Chart Loss
When converting `.xlsb` files to `.xlsx`, embedded charts are DROPPED by openpyxl/pyxlsb.
If the source xlsb has charts, you must either:
- Open it in Excel and save as xlsx manually
- Or rebuild the charts from the extracted data using openpyxl

Before overwriting source data, always verify you've captured it:
```python
# Before clearing, snapshot the original data
for row in range(1, min(ws.max_row + 1, 20)):
    vals = [ws.cell(row=row, column=c).value for c in range(1, min(ws.max_column + 1, 20))]
    if any(v is not None for v in vals):
        print(f"R{row}: {vals}")
```

### iFinD Data Quality
iFinD MCP responses may contain:
- `0x7` — internal error code (treat as missing)
- `抓取中...` — fetch in progress (treat as missing)
- Zero values where data should exist — always validate that 0 is ACTUALLY 0 vs. missing data
- Excel date serials (e.g. 37256) — convert with: `datetime(1899,12,30) + timedelta(days=int(serial))`

### Chart Duplication
When iterating on a sheet with charts, existing charts survive `.value = None` clearing.
To remove old charts before adding new ones:
```python
ws._charts = []  # clear all existing charts
```

## Sheet Organization Pattern (行业研究报告)

Recommend naming convention for multi-source merged workbooks:
```
Part1_全国数据
Part2_地方集群
Part3_重点公司
政策_xxx
测算_xxx
财务_营收净利润
财务_毛利率
财务_ROA
财务_资产负债率
财务_费用
财务_可比公司xxx
```
