#!/usr/bin/env python3
"""Reusable iFinD MCP query script.

Reads the JWE token from Hermes config.yaml at runtime (no embedded tokens).
Usage:
    /Users/eason/.hermes/hermes-agent/venv/bin/python3 scripts/ifind_query.py

Customize the 'queries' list below before running.
Key learning: Authorization header is the raw token — NO "Bearer" prefix.
"""

import yaml, subprocess, json
from pathlib import Path

# --- Configuration ---
config = yaml.safe_load(open(Path.home() / '.hermes' / 'config.yaml'))
token = config['mcp_servers']['hexin-ifind-ds-stock-mcp']['headers']['Authorization']

SERVICES = {
    'stock': 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-stock-mcp',
    'fund': 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-fund-mcp',
    'edb': 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-edb-mcp',
    'news': 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-news-mcp',
    'bond': 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-bond-mcp',
    'global_stock': 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-global-stock-mcp',
    'index': 'https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-index-mcp',
}

# --- Queries to run ---
# Format: (label, service_key, tool_name, query_string)
queries = [
    # Example queries — replace with your own:
    # ("revenue", "stock", "get_stock_financials", "沃尔德688028 2020到2025年 营业收入 净利润 ROE"),
    # ("products", "stock", "get_stock_summary", "沃尔德688028 主营业务 产品结构"),
    # ("macro", "edb", "get_edb_data", "中国PMI 2024 2025"),
]

# --- Execute ---
for label, svc_key, tool, query in queries:
    base = SERVICES[svc_key]
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {"name": tool, "arguments": {"query": query}}
    }
    # CRITICAL: raw token, NO "Bearer" prefix
    cmd = [
        "curl", "-s", "--max-time", "30", "-X", "POST", base,
        "-H", f"Authorization: {token}",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(payload)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=35)

    try:
        d = json.loads(r.stdout)
        if "result" in d:
            data = json.loads(d["result"]["content"][0]["text"])
            print(f"\n=== {label} ({svc_key}/{tool}) ===")
            print(json.dumps(data, ensure_ascii=False, indent=2)[:4000])
        else:
            print(f"\n=== {label} ({svc_key}/{tool}) ===\nERROR: {json.dumps(d, ensure_ascii=False)[:500]}")
    except Exception as e:
        print(f"\n=== {label} ===\nParse error: {e}\nRaw: {r.stdout[:500]}")
