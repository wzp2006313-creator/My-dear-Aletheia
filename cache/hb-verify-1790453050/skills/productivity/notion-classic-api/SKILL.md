---
name: notion-classic-api
description: "Write Notion pages/blocks via 2022-06-28 API urllib."
version: 1.0.0
platforms: [macos, linux, windows]
prerequisites:
  env_vars: [NOTION_API_KEY]
metadata:
  hermes:
    tags: [Notion, API, urllib, blocks, database]
---

# Notion Classic API (2022-06-28) — urllib write path

Reliable way to create pages in a Notion database with typed properties (title/select/status) and
structured blocks (headings, bullets, callouts, dividers) using Python `urllib` against the
**classic** API (`Notion-Version: 2022-06-28`).

## When to use this instead of the bundled `notion` skill

- The bundled `notion` skill states "**Python urllib is broken / DO NOT use urllib**". That is only
  true for `Notion-Version: 2026-03-11`. On `2022-06-28` urllib works reliably — proven on bulk
  casebook → Notion ingestion (dozens of blocks per page, all verified).
- `curl` / `ntn` / `subprocess` hit SSL timeouts (common on macOS system Python) — urllib + the
  right interpreter does not.

## Critical: pick the right Python interpreter

On macOS the system Python (`/usr/bin/python3`) ships **LibreSSL 2.8.3**, which fails the TLS
handshake to `api.notion.com` with `ConnectionResetError: [Errno 54] Connection reset by peer`.
The Hermes venv Python carries modern OpenSSL and connects fine:

```bash
~/.hermes/hermes-agent/venv/bin/python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"  # OpenSSL 3.x ✓
/usr/bin/python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"                          # LibreSSL 2.8.3 ✗
```

Run the write script with `~/.hermes/hermes-agent/venv/bin/python3` (or `executable_interpreter`
from the Hermes config) — NOT the bare `python3` on PATH.

## Steps

1. **Probe reachability** before any write: `GET /v1/users/me` (urllib, `Notion-Version: 2022-06-28`).
   Returns the bot name → SSL + token + version are all good.
2. **Create the page**: `POST /v1/pages` with `parent: {"database_id": DB_ID}` and typed properties.
3. **Append blocks**: `PATCH /v1/blocks/{page_id}/children` with `{"children": [...]}` — max 100
   blocks per request; chunk at 20 for reliability.
4. **Verify**: `GET /v1/blocks/{page_id}/children?page_size=100` → `len(results) > 0` means the write
   landed; `GET /v1/pages/{page_id}` confirms typed properties (e.g. `select.name`, `status.name`).

Ready-made block-builder helper (`create_page`, `append_blocks`, H1/H2/H3/P/B/callout/divider):
`references/block-builder-helper.md`.

## Pitfalls

- **API version is the whole game.** `2022-06-28` uses `POST /v1/pages`,
  `PATCH /v1/blocks/{id}/children`, `POST /v1/databases/{id}/query`. The 2026-03-11
  `/data_sources/` and `/pages/{id}/markdown` endpoints do NOT exist on 2022-06-28.
- **`select` properties** must name an option that already exists on the database schema — a new
  value fails the request.
- **Rich-text `content` cap ~2000 chars** per text object. Use `\n` inside a single object for line
  breaks (Notion renders them); split very long text into multiple objects/blocks.
- **Two-interpreter split**: if a library (e.g. `pymupdf` for PDF text) exists only in the system
  Python, extract content there, then write to Notion via the venv Python. Pass data through a
  script file, never shell args — special characters break shell parsing.
- **Tables** (对比表格/数据表): build a `table` block whose `table.children` is a list of
  `table_row` blocks (each `table_row.cells` = list of rich-text arrays, one per column). Set
  `table_width` = column count, `has_column_header: true`. The `table` + its `table_row` children
  are written as ONE nested block — they don't count separately against the 100-block chunk.
  **Verify trap**: `GET /v1/blocks/{page_id}/children` returns the `table` block WITHOUT its
  `table_row` children — query `GET /v1/blocks/{table_id}/children` separately to read the rows.
