# Notion API Integration

When user has Notion API key configured (`NOTION_API_KEY` env var), write content to Notion pages via API.

## Finding a Page
```bash
curl -s -X POST "https://api.notion.com/v1/search" \
  -H "Authorization: Bearer $NOTION_API_KEY" \
  -H "Notion-Version: 2022-06-28" \
  -H "Content-Type: application/json" \
  -d '{"query":"<page title>","filter":{"property":"object","value":"page"}}'
```
Returns page object with `id` field.

## Appending Blocks
```python
import json, os, subprocess

PAGE_ID = "<page-id>"
API_KEY = os.environ["NOTION_API_KEY"]

def append_blocks(blocks):
    url = f"https://api.notion.com/v1/blocks/{PAGE_ID}/children"
    subprocess.run(["curl","-s","-X","PATCH",url,
        "-H",f"Authorization: Bearer {API_KEY}",
        "-H","Notion-Version: 2022-06-28",
        "-H","Content-Type: application/json",
        "-d",json.dumps({"children":blocks})],
        capture_output=True, text=True)
```

## Block Types
- `heading_1`, `heading_2`, `heading_3` — section headers
- `paragraph` — body text
- `bulleted_list_item` — bullet points
- `callout` — highlighted box with emoji icon
- `divider` — horizontal line
- `quote` — indented quote block

## Table Blocks（对比表格）

写表格用 table block（含 table_row children 嵌套结构，一次性写入）：

```python
def make_table(header, rows):
    width = len(header)
    tr = lambda cells: {"object": "block", "type": "table_row",
                        "table_row": {"cells": [[text(c)] for c in cells]}}
    children = [tr(header)] + [tr(r) for r in rows]
    return {"object": "block", "type": "table", "table": {
        "table_width": width, "has_column_header": True,
        "has_row_header": False, "children": children}}
```

- table 的 children 是 table_row blocks（嵌套在同一个 table block 里一次写入，不算顶层 blocks 数）
- 每个 table_row 的 `cells` 是 rich_text 数组的数组（每列一个 rich_text 数组）
- **查询时 table 的 children 不自动展开**：`blocks/{page_id}/children` 返回的 table block 不含 rows，需单独查 `blocks/{table_id}/children` 才能拿到内容
- 写中文表格要在 TableStyle 里 `('FONTNAME',(0,0),(-1,-1),'中文字体')`，否则单元格中文乱码

## Limits
- Max 100 blocks per call
- Batch in groups of ~10-15 blocks per call to avoid timeout
