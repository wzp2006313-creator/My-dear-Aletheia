---
name: ifind-integration
description: Configure, troubleshoot, and use iFinD (同花顺) data services through Hermes MCP. Covers MCP server setup with JWE auth, token renewal, available tool catalog, and common query patterns for A-share equity research.
---

# iFinD Integration

iFinD (同花顺) is the primary financial data platform for Chinese A-share equity research. This skill covers connecting iFinD to Hermes via MCP servers and using the tools effectively.

## Triggers

- User asks to configure iFinD, set up iFinD MCP, or connect iFinD account
- User provides iFinD MCP server JSON config
- iFinD MCP tools return auth errors (401, expired token)
- User needs to add new iFinD MCP services or refresh tokens
- User asks a question that requires Chinese financial data (stock data, news, economic indicators)

## MCP Server Setup

See `references/mcp-configuration.md` for the detailed step-by-step setup guide, config format, and pitfalls.

Quick summary:

1. iFinD provides MCP servers at `https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-{service}-mcp`
2. Auth uses JWE tokens passed directly in the `Authorization` header (raw token, no "Bearer" prefix)
3. All 7 services use the same token
4. The `hermes mcp add` interactive CLI doesn't handle JWE tokens well — write directly to config.yaml instead
5. Use Hermes venv Python (`~/.hermes/hermes-agent/venv/bin/python3`) which has PyYAML
6. Config key is `mcp_servers` (not `mcpServers`) at top level of config.yaml

## Available MCP Services

| Service | Tools | Key Use Cases |
|---------|-------|---------------|
| stock | 9 tools | Company summary, screening, financials, shareholders, events, ESG, risk |
| fund | — | Fund data |
| edb | 1 tool | Macro & industry economic indicators |
| news | 3 tools | Announcement search, news search, trending news |
| bond | — | Bond data |
| global-stock | — | HK/US stock data |
| index | — | Index data |

## Common Query Patterns

After MCP is configured and reloaded (`/reload-mcp` or new session):

- "查一下 [股票名] 的最新财务数据" → uses stock MCP `get_stock_financials`
- "搜一下 [公司名] 最近的公告" → uses news MCP `search_notice`
- "筛选 ROE > 15% 的 A 股" → uses stock MCP `search_stocks`
- "查中国 PMI 数据走势" → uses EDB MCP `get_edb_data`

## Direct API Access (when MCP tools aren't loaded)

When MCP servers are configured but the current session hasn't reloaded them yet, you can call the iFinD API directly via curl. The API uses JSON-RPC 2.0 over HTTP.

**CRITICAL:** The `Authorization` header value is the raw JWE token — do NOT add a "Bearer" prefix. The token from config.yaml is the complete header value as-is.

Use `write_file` to create a reusable Python script (see `scripts/ifind_query.py`), then run it with Hermes venv Python. This avoids embedding the token in terminal commands where shell variable expansion can truncate it:

```bash
/Users/eason/.hermes/hermes-agent/venv/bin/python3 /tmp/ifind_query.py
```

The response is a JSON-RPC envelope: `{"jsonrpc":"2.0","result":{"content":[{"text":"...","type":"text"}]},"id":1}`. On success, `result.content[0].text` contains the data as a JSON-encoded string (parse it with `json.loads()`). On failure, the envelope may contain an `error` object with code `-32001` ("Gateway authentication failed").

**Reliable Python pattern** — use `scripts/ifind_query.py` as a template. Write queries to a file via `write_file`, then execute with Hermes venv Python. Do NOT embed the token in heredocs or f-strings; always read from config.yaml at runtime:

```python
import yaml, subprocess, json
from pathlib import Path

config = yaml.safe_load(open(Path.home() / '.hermes' / 'config.yaml'))
token = config['mcp_servers']['hexin-ifind-ds-stock-mcp']['headers']['Authorization']
base = 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-stock-mcp'

# The token IS the full Authorization header — no "Bearer" prefix
auth_header = token  # NOT f'Bearer {token}'

payload = {"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_stock_financials","arguments":{"query":"沃尔德688028 营业收入 净利润"}}}

r = subprocess.run(
    ['curl','-s','--max-time','30','-X','POST',base,
     '-H',f'Authorization: {auth_header}',
     '-H','Content-Type: application/json',
     '-d',json.dumps(payload)],
    capture_output=True, text=True, timeout=35)

d = json.loads(r.stdout)
if "result" in d:
    data = json.loads(d["result"]["content"][0]["text"])
    # data is now a dict with the query results
```

**Service-specific quirks:**
- `stock` and `edb` MCP: reliable, consistently return data
- `news` MCP: frequently returns "Gateway authentication failed" (-32001) even with valid token — fall back to `web_search` for news/announcement data when this happens

See `references/direct-api-access.md` for the full tool catalog and query examples.

## Pitfalls

- **NO "Bearer" prefix**: The `Authorization` header value is the raw JWE token from config.yaml — do NOT prepend "Bearer ". This was discovered after repeated "Gateway authentication failed" errors. `hermes mcp test` shows the header as `Authorization: eyJh***-6AQ` (no prefix). Follow the same pattern in curl calls.
- **LLM formatter truncation**: The JWE token (~850 chars) gets silently truncated to `***` when embedded in `write_file` content or `terminal` heredocs. This is a systemic issue — the LLM text formatter cannot preserve long token strings in tool call bodies. Workaround: always read the token from config.yaml at runtime via a script that was written with `write_file` (the Python code itself doesn't embed the token — it reads it at execution time). Never embed the raw token in source code, heredocs, f-strings, or shell variables.
- **Token truncation in summaries**: When copying iFinD MCP JSON from conversation history/compaction, verify the JWE token is complete (5 dot-separated parts, ~850 chars). Compaction/summaries can truncate tokens — always use the raw original from the user's first message.
- **Config key**: Hermes uses `mcp_servers` (snake_case) in config.yaml, not `mcpServers` (camelCase from MCP standard JSON).
- **Python yaml**: System Python may not have PyYAML. Hermes venv at `~/.hermes/hermes-agent/venv/bin/python3` always does.
- **Token expiry**: JWE tokens expire. When 401 errors appear, user needs to generate a new token from iFinD platform.
- **"Bearer" prefix kills auth**: The Authorization header value is the raw JWE token — do NOT prefix it with "Bearer ". Hermes MCP test shows `Authorization: eyJh***-6AQ` (no prefix). Adding "Bearer " causes `Gateway authentication failed` (-32001). When calling via curl or subprocess, use `-H "Authorization: <raw_token>"`, not `-H "Authorization: Bearer <token>"`.
- **Reload required**: After editing config.yaml, run `/reload-mcp` or start a new session for tools to become available.
- **news MCP unstable**: The news MCP server frequently returns "Gateway authentication failed" (-32001) even with a valid token that works on stock/edb servers. Fall back to `web_search` for news/announcement queries.
