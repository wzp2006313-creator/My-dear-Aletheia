# Block-builder helper (Notion classic API, urllib)

Proven on macOS during casebook → Notion ingestion. Run with the Hermes venv Python
(`~/.hermes/hermes-agent/venv/bin/python3`) — see SKILL.md for why.

```python
import json, urllib.request, os

API_KEY = os.environ.get("NOTION_API_KEY")  # or parse ~/.hermes/.env
DB_ID   = "..."                              # database_id (create-page parent)

def _req(url, data=None, method="GET"):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Notion-Version", "2022-06-28")   # classic block API (NOT 2026-03-11)
    req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req, timeout=25)

def create_page(title, case_type):
    data = {"parent": {"database_id": DB_ID},
            "properties": {"Name": {"title": [{"text": {"content": title}}]},
                           "Case Type": {"select": {"name": case_type}}}}
    return json.loads(_req("https://api.notion.com/v1/pages", data, "POST").read())["id"]

def append_blocks(pid, blocks):
    # max 100 blocks/request; chunk at 20 for reliability
    for i in range(0, len(blocks), 20):
        _req(f"https://api.notion.com/v1/blocks/{pid}/children",
             {"children": blocks[i:i+20]}, "PATCH")

def verify(pid):
    r = _req(f"https://api.notion.com/v1/blocks/{pid}/children?page_size=100")
    return len(json.loads(r.read()).get("results", []))

# Block builders (return full block objects)
def T(s):   return {"type": "text", "text": {"content": s}}
def H1(s):  return {"object":"block","type":"heading_1","heading_1":{"rich_text":[T(s)]}}
def H2(s):  return {"object":"block","type":"heading_2","heading_2":{"rich_text":[T(s)]}}
def H3(s):  return {"object":"block","type":"heading_3","heading_3":{"rich_text":[T(s)]}}
def P(s):   return {"object":"block","type":"paragraph","paragraph":{"rich_text":[T(s)]}}
def B(s):   return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":[T(s)]}}
def C(s, emoji): return {"object":"block","type":"callout","callout":{"rich_text":[T(s)],"icon":{"emoji":emoji}}}
def DIV():  return {"object":"block","type":"divider","divider":{}}
YOUR     = lambda: C("YOUR ANSWER HERE", "\u270f\ufe0f")   # pencil
OFFICIAL = lambda s: C(s, "\ud83d\udccb")                   # clipboard
```

## Notes

- `POST /v1/pages` — parent is `database_id`; properties are typed (`title`, `select`, `status`,
  `date`, `number`, `rich_text`, …).
- Each block = `{"object":"block","type":<type>, <type>: {...}}`. Block types: `heading_1/2/3`,
  `paragraph`, `bulleted_list_item`, `numbered_list_item`, `callout`, `divider`, `to_do`, `quote`.
- `GET /v1/pages/{id}` returns `properties` — use it to confirm `select.name` / `status.name` landed
  (a bad `select` value fails the create; a `status` value not in the schema is ignored silently).
- `text.content` capped ~2000 chars per object; `\n` inside one object renders as line breaks.
- The 2022-06-28 query endpoint is `POST /v1/databases/{id}/query` (not `/data_sources/`).
