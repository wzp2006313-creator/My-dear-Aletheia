# Direct iFinD MCP API Access

Call iFinD MCP tools via JSON-RPC 2.0 over HTTP when the native MCP tools aren't loaded in the current session (e.g., after mid-session config changes before `/reload-mcp`).

## Stock MCP Tools (`hexin-ifind-ds-stock-mcp`)

| Tool | Description |
|------|-------------|
| `get_stock_summary` | Quick company overview: basic info, industry classification, main products |
| `search_stocks` | Natural language stock screening (e.g., "ROE > 15% 的超硬材料公司") |
| `get_stock_performance` | Daily price history, technical indicators, technical patterns |
| `get_stock_info` | Detailed company info: listing details, index membership, key classifications |
| `get_stock_shareholders` | Share capital structure, shareholder composition, actual controller |
| `get_stock_financials` | Financial statements + derived indicators (revenue, profit, margins, ROE, etc.) |
| `get_risk_indicators` | Quantitative risk: alpha, beta, volatility, VaR |
| `get_stock_events` | Corporate events: IPO, dividends, M&A, restructuring |
| `get_esg_data` | ESG ratings and reports |

### Query patterns

```json
// Financial data
{"query": "沃尔德688028 2020到2025年营业收入 净利润 毛利率 ROE"}

// Product/business info
{"query": "沃尔德688028 主营业务 产品结构 收入构成"}

// Shareholder structure
{"query": "沃尔德688028 股权结构 实际控制人持股"}

// Multi-company comparison
{"query": "四方达300179 沃尔德688028 近三年毛利率对比"}
```

## EDB MCP Tools (`hexin-ifind-ds-edb-mcp`)

| Tool | Description |
|------|-------------|
| `get_edb_data` | Macro & industry economic indicators: GDP, CPI, PMI, industrial output, etc. |

### Query patterns

```json
{"query": "中国制造业PMI 近一年走势"}
{"query": "中国超硬材料行业市场规模"}
```

## News MCP Tools (`hexin-ifind-ds-news-mcp`)

| Tool | Description |
|------|-------------|
| `search_notice` | Semantic search of A-share/HK/US company announcements |
| `search_news` | Financial news article search |
| `search_trending_news` | Hot event-driven news with high timeliness |

### Quirk

The news MCP has been observed to return `Gateway authentication failed` (-32001) even with a valid token that works for stock/EDB. When this happens, fall back to `web_search` for news queries.

### Query patterns

```json
// Company announcements
{"query": "沃尔德 CVD金刚石 散热片 半导体进展"}

// Industry news
{"query": "超硬刀具 行业趋势 2024 2025"}
```

## Response Format

All responses follow JSON-RPC 2.0:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"code\":1,\"msg\":\"success\",\"data\":{\"answer\":\"...\"}}"
      }
    ]
  }
}
```

The actual data lives in `result.content[0].text` as a JSON string — parse it twice:

```python
result = json.loads(response_text)
outer = json.loads(result['result']['content'][0]['text'])
data = outer['data']['answer']  # markdown table or text
```

Error responses:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32001,
    "message": "Gateway authentication failed: Gateway authentication failed"
  }
}
```
