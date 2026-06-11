# iFinD MCP Server Configuration

Step-by-step guide for connecting iFinD data services to Hermes via MCP.

## Prerequisites

- iFinD account with MCP access enabled
- JWE Bearer token (obtained from iFinD platform)
- Hermes Agent installed

## Config Format

Each MCP server entry in `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  hexin-ifind-ds-stock-mcp:
    headers:
      Authorization: "<JWE_TOKEN>"
    type: streamablehttp
    url: https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-stock-mcp
```

Key notes:
- Top-level config key is `mcp_servers` (snake_case), NOT `mcpServers`
- Auth is a JWE token (5 dot-separated parts, ~850 chars) passed as `Authorization: Bearer <token>` format via the `headers.Authorization` field
- Type is `streamablehttp`
- All 7 services share the same token

## All 7 Server URLs

```
hexin-ifind-ds-stock-mcp:        https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-stock-mcp
hexin-ifind-ds-fund-mcp:         https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-fund-mcp
hexin-ifind-ds-edb-mcp:          https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-edb-mcp
hexin-ifind-ds-news-mcp:         https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-news-mcp
hexin-ifind-ds-bond-mcp:         https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-bond-mcp
hexin-ifind-ds-global-stock-mcp: https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-global-stock-mcp
hexin-ifind-ds-index-mcp:        https://api-mcp.51ifind.com:8643/ds-mcp-servers/hexin-ifind-ds-index-mcp
```

## Step-by-Step Setup

### 1. Write config directly (recommended)

The `hermes mcp add` CLI is interactive and doesn't handle JWE tokens cleanly. Instead, write to config.yaml directly:

```bash
# Use Hermes venv Python (has PyYAML)
~/.hermes/hermes-agent/venv/bin/python3 << 'PYEOF'
import yaml, json
from pathlib import Path

config_path = Path.home() / '.hermes' / 'config.yaml'

with open(config_path) as f:
    config = yaml.safe_load(f)

# Replace with actual JWE token
TOKEN = "<full_jwe_token_here>"

services = ["stock", "fund", "edb", "news", "bond", "global-stock", "index"]

if 'mcp_servers' not in config:
    config['mcp_servers'] = {}

for svc in services:
    name = f"hexin-ifind-ds-{svc}-mcp"
    config['mcp_servers'][name] = {
        'headers': {'Authorization': TOKEN},
        'type': 'streamablehttp',
        'url': f"https://api-mcp.51ifind.com:8643/ds-mcp-servers/{name}"
    }

with open(config_path, 'w') as f:
    yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

print("Done")
PYEOF
```

### 2. Verify

```bash
hermes mcp list                    # Should show all 7 servers
hermes mcp test hexin-ifind-ds-stock-mcp  # Test connection + tool discovery
```

### 3. Reload

In an active session: `/reload-mcp`
Or start a new session to pick up the new tools.

## Troubleshooting

### 401 Unauthorized

- Token is expired (JWE tokens have limited lifetime). Generate a new one from iFinD.
- Token is truncated. Verify it has exactly 5 dot-separated parts and ~850 characters. Compaction or copy-paste can corrupt long tokens.
- Check the raw `Authorization` value in config.yaml — Hermes displays it truncated in logs (`eyJh***-6AQ`) but the full value must be present.

### 404 or connection refused

- Verify the URL matches exactly the pattern above
- iFinD MCP requires port 8643 — ensure firewall allows outbound HTTPS to this port

### Python yaml not found

System Python may not have PyYAML. Always use Hermes venv Python:
```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "import yaml; print('OK')"
```

### Token format validation

A valid JWE token has this structure:
```
<base64_header>.<base64_encrypted_key>.<base64_iv>.<base64_ciphertext>.<base64_tag>
```
5 parts, separated by dots. Example header decodes to `{"alg":"RSA-OAEP-256","enc":"A256GCM"}`.

## What NOT to do

- Don't use `hermes mcp add --auth header` — the interactive prompt doesn't work well with JWE tokens.
- Don't use system Python without PyYAML — use Hermes venv.
- Don't use `mcpServers` (camelCase) as the config key — Hermes expects `mcp_servers`.
