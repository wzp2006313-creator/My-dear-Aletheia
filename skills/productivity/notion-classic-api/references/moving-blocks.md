# Moving / copying blocks & pages (bulk migration)

Learned during a Peter K casebook → Notion migration (11 database rows turned into sub-pages of a
single "casebook" page). All on `Notion-Version: 2022-06-28` + urllib + the Hermes venv Python.

## Three 400-error traps

1. **Never re-send a block's raw JSON back to Notion.**
   `GET /v1/blocks/{id}/children` returns each block with `id`, `parent`, `created_time`,
   `last_edited_time`, `created_by`, `last_edited_by`, `annotations`, `link: null`, `has_children`,
   `in_trash`, `archived`, etc. Re-POSTing that verbatim → `400 validation_error`.

   **Fix — rebuild every block by type.** Keep only `object` + `type` + the type's payload, and
   reduce `rich_text` entries to `{"type":"text","text":{"content": rt["plain_text"]}}`. For
   `callout`, keep `icon` as `{"emoji": ...}` only. Drop `heading_1` when the destination already
   carries a title (e.g. a sub-page whose title is set at creation). Skeleton:

   ```python
   def rebuild(b):
       t = b["type"]
       if t in ("heading_2","heading_3","paragraph","bulleted_list_item","numbered_list_item","quote"):
           return {"object":"block","type":t, t:{"rich_text":[{"type":"text","text":{"content":rt.get("plain_text","")}} for rt in b[t]["rich_text"]]}}
       if t == "callout":
           icon = b["callout"].get("icon")
           if icon and icon.get("emoji"): icon = {"emoji": icon["emoji"]}
           c = {"rich_text":[{"type":"text","text":{"content":rt.get("plain_text","")}} for rt in b["callout"]["rich_text"]]}
           if icon: c["icon"] = icon
           return {"object":"block","type":"callout","callout":c}
       if t == "divider":
           return {"object":"block","type":"divider","divider":{}}
       return None
   ```

2. **Creating a child page = `POST /v1/pages`, NOT a `child_page` block.**
   A `{"type":"child_page","child_page":{"title":...}}` block appended to a parent page returns
   `400` ("child_page should be defined"). Correct way:

   ```python
   data = {"parent": {"type":"page_id","page_id": PARENT_PAGE_ID},
           "properties": {"title": {"title": [{"text":{"content": TITLE}}]}}}
   # POST https://api.notion.com/v1/pages  ->  json["id"] is the new sub-page id
   ```

3. **Delete / archive = `PATCH /v1/pages/{id}` with `{"archived": true}`.**
   There is no working `DELETE /v1/pages/{id}` on 2022-06-28 — it returns `400`.

## Migration recipe (database row → sub-page of some page)

1. `POST /v1/databases/{id}/query` → source page id + typed props (title/select/status).
2. `GET /v1/blocks/{src}/children` → read all blocks.
3. `POST /v1/pages` (parent = target page id) → create sub-page; its title carries the label
   (e.g. `"Case 6 — Banknote (Revenue growth)"`).
4. Rebuild blocks (trap 1), skip the `heading_1` title, `PATCH` into the new page in chunks of 20.
5. `PATCH /v1/pages/{src}` `{"archived": true}` → retire the original database row.

## De-dup warning

`[Errno 54] Connection reset by peer` is common mid-migration. On retry, note that step 3 (create
sub-page) may have already succeeded even when step 4 threw — so the retry creates a *duplicate*
sub-page. After migrating, re-list the parent's children and archive any sub-page whose title
repeats; keep the one with the highest block count.

## Also seen this session

- Free image hosts (catbox.moe, 0x0.st) were unavailable / upload-disabled — there is **no**
  reliable way to push a local image into a Notion `image` block via the classic API (only
  `external` URLs are accepted; no public upload endpoint). Render PNGs locally and hand them to
  the user to drag in, instead of fighting this.
