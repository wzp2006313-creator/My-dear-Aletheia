# Notion Delivery Pattern for Follow Builders

When the digest delivery method is Notion, the agent must:
1. Update the daily archive table (add today's row)
2. Append the full digest markdown to the page

## Pitfall: Shell `$()` subshell evaluation in Hermes terminal

Hermes' shell evaluator processes `$()` BEFORE passing commands to bash. This means you CANNOT use subshell syntax like:

```bash
# WRONG — Hermes pre-evaluates the $() and breaks
NOTION_API_TOKEN=*** .hermes/.env | cut -d= -f2-)
```

When Hermes sees `$()`, it tries to evaluate the expression in its own evaluator context, which fails because the inner command references paths and tools that don't exist in that context.

## Workaround: Python subprocess for key extraction + curl

Use a Python script that extracts the key via subprocess and then calls curl directly. The Python interpreter receives the shell command as a string literal, so `$()` is never evaluated by Hermes' shell.

### Pattern: Extract key + call Notion API

```python
import subprocess, json, os

# 1. Extract API key from .env
r = subprocess.run(
    "grep NOTION_API_KEY /Users/eason/.hermes/.env",
    shell=True, capture_output=True, text=True
)
token = r.stdout.strip().split('=', 1)[1]

# 2. Optional: set env for ntn CLI
os.environ['NOTION_API_TOKEN'] = token
os.environ['NOTION_KEYRING'] = '0'

# 3. Call Notion API via curl
page_id = "YOUR_PAGE_ID"
auth = "Bearer " + token

def patch_markdown(body):
    return subprocess.run([
        "curl", "-s", "-X", "PATCH",
        f"https://api.notion.com/v1/pages/{page_id}/markdown",
        "-H", f"Authorization: {auth}",
        "-H", "Notion-Version: 2026-03-11",
        "-H", "Content-Type: application/json",
        "-d", json.dumps(body)
    ], capture_output=True, text=True, timeout=60)
```

### Example: Update table row + append digest

```python
# Step 1: Add today's date row to archive table
table_body = {
    "type": "update_content",
    "update_content": {
        "content_updates": [{
            "old_str": "<td>2026-06-03</td>\n<td>✅ 完成</td>\n</tr>\n</table>",
            "new_str": "<td>2026-06-03</td>\n<td>✅ 完成</td>\n</tr>\n<tr>\n<td>2026-06-04</td>\n<td>✅ 完成</td>\n</tr>\n</table>"
        }]
    }
}
r1 = patch_markdown(table_body)

# Step 2: Append digest
digest = open('/tmp/fb-digest-YYYY-MM-DD.md').read()
append_body = {
    "type": "insert_content",
    "insert_content": {"content": digest}
}
r2 = patch_markdown(append_body)

# Step 3: Verify
r3 = subprocess.run([
    "curl", "-s",
    f"https://api.notion.com/v1/pages/{page_id}/markdown",
    "-H", f"Authorization: {auth}",
    "-H", "Notion-Version: 2026-03-11",
], capture_output=True, text=True, timeout=30)
data = json.loads(r3.stdout)
if "AI Builders Digest" in data.get("markdown", ""):
    print("VERIFIED")
```

### Common Notion API payloads for this workflow

**update_content** — targeted search-and-replace (use for table updates):
```json
{
  "type": "update_content",
  "update_content": {
    "content_updates": [
      {"old_str": "exact text to find", "new_str": "replacement text"}
    ]
  }
}
```

**insert_content** — append to end of page (use for new digest):
```json
{
  "type": "insert_content",
  "insert_content": {
    "content": "markdown content here"
  }
}
```

**replace_content** — replace entire page (use only for full rewrites):
```json
{
  "type": "replace_content",
  "replace_content": {
    "new_str": "complete new markdown"
  }
}
```

### Why not use ntn CLI directly?

`ntn` CLI works but requires the token in env vars. The `$()` shell pitfall applies equally to setting env vars with `ntn`. The Python subprocess approach is the most reliable method when running under Hermes cron jobs.
