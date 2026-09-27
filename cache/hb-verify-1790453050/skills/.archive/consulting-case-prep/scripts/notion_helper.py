"""
Notion write helper — classic API (Notion-Version: 2022-06-28) via urllib.request.

Verified working on this user's macOS setup. Do NOT use curl-via-subprocess
(SSL handshake timeouts) or inline `python3 -c` (triggers "embedded null byte").

Usage (in a standalone .py file):
    import sys; sys.path.insert(0, "/tmp")   # or wherever this file lives
    from notion_helper import create_page, append_blocks, standard_header, H2, H3, P, B, C, DIV, YOUR, OFFICIAL
    pid = create_page("Mck-Case Name", "Profitability")
    append_blocks(pid, standard_header("Case Name — McKinsey 2020", "Profitability", "Time: 30 min | Interviewer-driven")
                       + [H2("Prompt"), P("..."), DIV(), H2("Case Questions")])
"""
import json, urllib.request, os

API_KEY = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_API_TOKEN")
if not API_KEY:
    try:
        for line in open(os.path.expanduser("~/.hermes/.env")):
            line = line.strip()
            if line.startswith("NOTION_API_KEY="):
                API_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")
                break
    except Exception:
        pass

DB_ID = "329fde4c-8055-807d-a29d-cb206d82671a"
API_VER = "2022-06-28"


def _req(url, data=None, method="GET"):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method)
    req.add_header("Authorization", f"Bearer {API_KEY}")
    req.add_header("Notion-Version", API_VER)
    req.add_header("Content-Type", "application/json")
    return urllib.request.urlopen(req, timeout=25)


def create_page(title, case_type, db_id=DB_ID):
    data = {
        "parent": {"database_id": db_id},
        "properties": {
            "Name": {"title": [{"text": {"content": title}}]},
            "Case Type": {"select": {"name": case_type}},
            "Status": {"status": {"name": "Mentorship"}},
        },
    }
    r = _req("https://api.notion.com/v1/pages", data, "POST")
    return json.loads(r.read())["id"]


def append_blocks(pid, blocks):
    # Notion caps 100 blocks/request; chunk at 20 for reliability
    for i in range(0, len(blocks), 20):
        _req(f"https://api.notion.com/v1/blocks/{pid}/children", {"children": blocks[i:i + 20]}, "PATCH")


def archive_page(pid):
    _req(f"https://api.notion.com/v1/pages/{pid}", {"archived": True}, "PATCH")


def list_children(pid):
    r = _req(f"https://api.notion.com/v1/blocks/{pid}/children?page_size=100")
    return json.loads(r.read()).get("results", [])


# block builders
def T(s): return {"type": "text", "text": {"content": s}}
def H1(s): return {"object": "block", "type": "heading_1", "heading_1": {"rich_text": [T(s)]}}
def H2(s): return {"object": "block", "type": "heading_2", "heading_2": {"rich_text": [T(s)]}}
def H3(s): return {"object": "block", "type": "heading_3", "heading_3": {"rich_text": [T(s)]}}
def P(s): return {"object": "block", "type": "paragraph", "paragraph": {"rich_text": [T(s)]}}
def B(s): return {"object": "block", "type": "bulleted_list_item", "bulleted_list_item": {"rich_text": [T(s)]}}
def C(s, emoji): return {"object": "block", "type": "callout", "callout": {"rich_text": [T(s)], "icon": {"emoji": emoji}}}
def DIV(): return {"object": "block", "type": "divider", "divider": {}}


def YOUR(): return C("YOUR ANSWER HERE", "\u270f\ufe0f")   # pencil — blank slot for the user
def OFFICIAL(s): return C(s, "\ud83d\udccb")              # clipboard — condensed official answer


def standard_header(title, case_type, meta):
    """Standard opening blocks for a case page."""
    return [
        H1(title),
        C(f"Case Type: {case_type} | Source: Peter K 2020 Casebook | {meta}", "\ud83d\udcd6"),
        DIV(),
    ]
