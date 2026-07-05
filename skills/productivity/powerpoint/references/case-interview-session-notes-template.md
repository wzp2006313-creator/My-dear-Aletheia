# Case Interview Session — Structured Notes Template

When the user sends PPT case materials + detailed meeting notes and asks you to organize them into a reference document, follow this structure.

## Trigger

User sends one or more `.pptx` case files plus plain-text meeting notes and says: "整理一下" / "organize this" / "combine these".

## Workflow

1. **Extract PPT content** — use `python-pptx` to dump all slide text:
   ```python
   from pptx import Presentation
   prs = Presentation("case.pptx")
   for i, slide in enumerate(prs.slides, 1):
       for shape in slide.shapes:
           if hasattr(shape, 'text') and shape.text.strip():
               print(shape.text.strip())
   ```

2. **Merge with meeting notes** — the PPT provides the case framework (questions, assumptions, data tables); the meeting notes provide corrections, coaching feedback, and personal takeaways. The notes are authoritative where they contradict the PPT.

3. **Structure the final document** with these sections (in order):

   - **Case title + subtitle** — "Case Name — Market Entry / Profitability / etc."
   - **题目 (Prompt)** — the case question in one paragraph
   - **Clarification Questions & 战略目标** — what was asked, what the client's objectives are (more than just "make money")
   - **Framework** — the complete opening architecture, not just buckets but the storytelling sequence
   - **Q1: [question]** — assumptions table, revenue tree, calculations, profit result
   - **Q2: [question]** — same structure for each sub-question
   - **NPV analysis** (if applicable) — calculation, interpretation, "面试级表达" (the polished English version)
   - **Additional considerations** — what else the client should think about
   - **Coach feedback** — corrections about framework, calculations, communication style
   - **Homework / 重做任务** — specific re-do tasks assigned
   - **一句话总结** — the single key takeaway from the session
   - **附录 (Appendix)** — any other cases mentioned but not covered

4. **Output formats:**
   - Save as `.md` to `~/Downloads/`
   - Upload to Notion using the `notion` skill (create page as child of a relevant parent page)

## Style rules

- User prefers natural Chinese, minimal markdown formatting in casual chat — but in documents, clean markdown headings and tables are fine
- Number-heavy sections: use tables, not prose
- Coaching feedback: put in `> blockquote` or `<callout>` to visually separate from case content
- Key numbers (NPV, profit, revenue) should be bolded for scanability
- Include both the raw calculation AND the polished English interview answer for NPV/strategic conclusions

## Data integrity

- PPT numbers are the starting framework
- Meeting notes corrections OVERRIDE the PPT where they disagree
- Flag any assumptions that weren't verified in the session
