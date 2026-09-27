---
name: consulting-case-prep
description: "Organize consulting case-interview cases into Notion pages."
version: 1.0.0
author: curator
license: MIT
metadata:
  hermes:
    tags: [consulting, case-interview, notion, mckinsey, bain, bcg, casebook]
    category: productivity
---

# Consulting Case Prep — Notion Organization

The user (展鹏, 宋瀚清) is preparing for consulting interviews (coach: Shelley) and keeps a Notion database of cases. Recurring tasks: extract cases from casebook PDFs (e.g. Peter K 2020), summarize coaching-session transcripts, and organize everything into Notion pages — one page per case, with a blank "YOUR ANSWER" slot next to every question plus the official answer.

## When to Use

Trigger when the user asks to: organize a casebook or case interview into Notion, extract cases from a PDF (Peter K, other casebooks), write a coaching-session summary into their "咨询准备" / "Prep List" database, or build "case pages" with blank answer slots + official answers. Also use whenever writing to the user's Notion case-prep database via the classic API.

## Notion database

- **Database ID:** `329fde4c-8055-807d-a29d-cb206d82671a` (parent "咨询准备" / "Prep List").
- **Properties:** `Name` (title), `Case Type` (select: Profitability / Market Entry / Revenue growth / Comparison / PE firm / Wild card / Other), `Status` (status → set to `Mentorship`), plus `Type`, `Select`, `Date`, `URL`.
- **Page naming convention:** `Mck-<Case English Name>` (e.g. `Mck-Diesel Truck Manufacturer`, `Mck-European Beauty Company`).

## Case page format (fixed — user approved)

```
H1  <Case Name — Firm Year>
callout  "Case Type: X | Source: Peter K 2020 Casebook | Time: XX min | Interviewer-driven"
divider
H2  Prompt
P   <full prompt text>
P   Key facts (from "Additional information")
divider
H2  Case Questions
H3  Q1: <question text>
callout ✏️  "YOUR ANSWER HERE"     ← left blank for the user to fill (no prefix)
callout 📋  "OFFICIAL: <condensed official answer>"   ← literal "OFFICIAL: " text prefix, matches the reference page
... repeat per question
```

The official answer must be **condensed to key points** (keep the critical numbers, the math steps, and the conclusion; drop the verbose scaffolding). Math questions keep the full calculation chain and the final number.

## Working Notion write technique (VERIFIED — use this, not the `notion` skill's advice)

The community `notion` skill pushes `Notion-Version: 2026-03-11` + `ntn` CLI and claims Python `urllib` is broken. For THIS user's setup, the reliable path is the **classic API + `urllib.request` in a standalone `.py` file**:

- Header `Notion-Version: 2022-06-28` (classic endpoints: `/v1/databases/{id}/query`, `/v1/blocks/{id}/children`).
- `urllib.request` with `Authorization: Bearer $NOTION_API_KEY` works. Auth key lives in `~/.hermes/.env` as `NOTION_API_KEY` (also `NOTION_API_TOKEN`, `NOTION_KEYRING`).
- **Write the script to a file (`write_file` → `python3 /tmp/x.py`), never inline `python3 -c "..."`.** Inline `-c` triggers the Hermes terminal tool's "embedded null byte" guard and is rejected.
- Append blocks in **chunks of ≤20** per `PATCH /v1/blocks/{id}/children` request (large single batches time out).
- **Archive** via `PATCH /v1/pages/{id}` with `{"archived": true}` — `DELETE /v1/pages/{id}` returns 400.
- `curl` directly in shell works; `curl` via Python `subprocess.run()` intermittently SSL-handshake-times-out — avoid it, use `urllib`.

## Pitfalls

- **Two API versions behave differently.** 2022-06-28 (`urllib` fine, `archived` PATCH fine, `/databases` endpoint) vs 2026-03-11 (`urllib` → `invalid_request_url`, `archived` rejected, `/data_sources` endpoint, `ntn` preferred). Pick one and stay consistent. This session proved 2022-06-28 + `urllib` works end-to-end.
- **Never `DELETE` a page** — Notion has no DELETE; use archive (PATCH `archived: true`). Clean up test pages with archive, not delete.
- **Verify after writing.** After appending blocks, `GET /v1/blocks/{pid}/children` and confirm the block count / headings. `urllib` can silently succeed on the create but drop a late batch on SSL timeout — re-send the failed chunk.
- The Notion search endpoint (`POST /v1/search`) is slowest / most likely to time out; query the database directly when you already know the DB ID.
- **Extract PDF text via `terminal` python3, not the `execute_code` sandbox.** The sandbox interpreter lacks `pymupdf`; the terminal venv has it. Per-page extraction: `import pymupdf; doc = pymupdf.open('/tmp/peterk.pdf'); doc[i].get_text()` (also `/tmp/peterk_full.txt` has `===PAGE N===` markers for quick grepping). The notion_helper script needs `urllib` only, so it runs fine in either — but do everything in one terminal `python3` run.
- **Source casebooks carry copy-paste artifacts.** The Almond farm Q3 math slide contained a leftover "digital solution / beauty advisor costs" line from another case. Extract the *correct* calculation (2,550M lbs × 1.4 × $2.00 = $7.2B), never propagate the artifact into Notion.
- **Question numbering in the source overview can be out of order** (Fast casual food restaurant lists Q7 before Q3 in its overview). Present questions in logical 1..N order on the page.
- **Subagent parallelism collides on shared `/tmp` filenames.** This batch is split across subagents all writing scripts; use a unique script filename (e.g. `write_cases_5678.py`), and `cp` to it before running so a sibling's overwrite can't corrupt your in-flight run.

## Reference

`references/peterk-casebook.md` — the 11-case Peter K 2020 table of contents with PDF page ranges and case types, for re-running batch extraction.
