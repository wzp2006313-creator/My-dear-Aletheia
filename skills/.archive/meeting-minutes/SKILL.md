---
name: meeting-minutes
description: Convert raw meeting transcripts, voice recordings, or free-form notes into structured Q&A-style meeting minutes in docx format. Use when the user provides a meeting transcript, call recording notes, or散乱会议记录 and asks to "整理成纪要", "输出成会议纪要", "按四方达格式整理", or similar.
---

# Meeting Minutes Conversion

## Triggers

- User provides a transcript, recording notes, or free-form meeting text
- User asks to "整理成纪要", "输出成调研纪要", "转成会议纪要格式"
- User references an existing meeting minutes format and says "按这种格式输出"

## Target Format

Docx (.docx) with the following structure, modeled on 四方达调研纪要 format:

1. **Title**: `{公司名称} {会议主题} 交流纪要` — centered, bold, 14pt, 楷体
2. **Meta lines**: 时间 / 主讲人 / 参会方 / 形式 — 11pt, 楷体
3. **Q&A blocks**: Numbered questions in bold, answers in normal weight. Questions and answers use 11pt 楷体. Single space between blocks.

Memory note: user prefers 楷体 GB2312 11pt for meeting minutes, no extra markdown files.

## Workflow

### Step 1: Parse the transcript

Read the raw text. Identify:
- Who is speaking (speaker labels)
- What are the natural topic blocks
- Which questions were explicitly asked
- Which answers need to be extracted from monologue sections

For transcripts that are mostly monologue/presentation (like the 天禄科技 TAC膜 case), extract logical Q&A pairs by grouping related content under question headers. The questions should be the natural ones an investor/analyst would ask about each topic.

### Step 2: Structure into Q&A

Transform raw content into crisp Q&A pairs. Rules:
- Each Q&A covers one coherent topic
- Answers use the speaker's own data points and language, not paraphrased summaries
- Remove filler words (um, uh, "就是说", "是这样的"), keep the substance
- Keep specific numbers, dates, company names, and direct quotes intact
- If a question wasn't literally asked but the speaker covered the topic, formulate an appropriate question
- Target 8-12 Q&A pairs for a typical 1-hour meeting

### Step 3: Generate docx

Use `docx-js` (npm package `docx`). Template reference at [`templates/qa-meeting-minutes.js`](templates/qa-meeting-minutes.js).

Key formatting:
- Font: 楷体 (KaiTi) throughout
- Title: centered, 14pt, bold
- Meta lines: 11pt
- Q&A: question in bold 11pt with numbering, answer in normal 11pt with first-line indent
- End with right-aligned "纪要整理：AI辅助生成，经人工核对" in small gray italic
- Page size: A4 (11906 × 16838 DXA), 1-inch margins

### Step 4: Validate and deliver

After creating the docx:
1. Confirm file saved to user's specified location
2. List the Q&A topics so user can quickly verify coverage
3. Ask if adjustments needed

## Pitfalls

- **Don't use markdown for the final output** — the user wants docx, not .md. The memory explicitly states "会议纪要默认 Word 格式".
- **Don't fabricate data** — if the transcript has gaps (missing numbers, unclear timelines), note them but don't fill in with guesses.
- **Keep speaker's tone** — the answers should read like the speaker is talking, not like a third-party summary. Use direct quotes of key statements.
- **Factual accuracy over elegance** — wrong numbers are worse than rough prose. Verify key figures before writing.
- **Chinese font consistency** — 楷体 must be used throughout. Mixing fonts (e.g. default Arial falling back) is not acceptable.

## docx-js Setup

```bash
npm install -g docx
# If global install doesn't resolve, install locally:
cd /path/to/output && npm install docx
# Run with NODE_PATH if needed.
# On this user's macOS, global npm root is /Users/eason/.npm-global/lib/node_modules:
NODE_PATH=/Users/eason/.npm-global/lib/node_modules node script.js
```

## PDF Source Handling

When the source file is a PDF (e.g., reference meeting minutes), extract text with pymupdf:

```bash
python3 -c "
import fitz
doc = fitz.open('/path/to/file.pdf')
for page in doc:
    print(page.get_text())
doc.close()
"
```

Never use `read_file` directly on PDFs — they render as binary gibberish.

## Template

See `templates/minutes.js` for the canonical docx-js generation script. Copy and modify it for each new meeting minutes document.
