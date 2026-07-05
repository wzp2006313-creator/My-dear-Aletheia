# Consulting Research PPT Patterns

Common slide structures for Chinese consulting/industry research intern candidates.

## Pattern 1: Market Overview Slide

Structure:
- Top: Header bar (dark navy #1E3A5F) + title + subtitle
- Row 1: 3-4 metric cards (population, penetration, index, etc.) with source tags
- Row 2: Stage assessment text block with key judgment
- Row 3: 2-3 opportunity signal cards

PowerPoint: `add_shape(RECTANGLE)` for cards, `add_text_box` for content.
Python-pptx preferred over pptxgenjs for reliability.

## Pattern 2: Policy & Strategy Slide

Structure:
- Left panel: Strategic axes as numbered list with colored accent bars
- Right panel: Milestone timeline + key institutions with description
- Bottom: Source footer bar

## Pattern 3: Construction Focus & Challenges (Two-Column)

Structure:
- Left column: "What they are building" — numbered priority cards
- Right column: "What holds them back" — challenge cards with different accent color
- Bottom: Implication bar

Each card: white bg, thin grey border, colored left accent bar (0.06"), title + body text.

## Pattern 4: Client & Opportunity Mapping

Structure:
- Section 1: Policy agencies (strategic partners) — name + importance + approach
- Section 2: Core partners (operators/SOEs) — name + desc + hardware match
- Section 3: Demand→Product mapping table (2 columns: government need vs hardware)

## Pattern 5: Competition & Entry Strategy

Structure:
- Left: Competitor analysis (5-6 rows, each with name + position + detail)
- Right: Product-market fit matrix (product + star rating + rationale)
- Bottom: Key conclusions + 3 action recommendations in gold-bordered box

## Common Color Palette (Intern-grade)

```python
WHITE = RGBColor(0xFF,0xFF,0xFF)
BG = RGBColor(0xFA,0xFB,0xFC)      # off-white
HEADER_BG = RGBColor(0x1E,0x3A,0x5F) # dark navy header
ACCENT = RGBColor(0x1A,0x52,0x76)   # muted blue
GOLD = RGBColor(0xB8,0x86,0x0B)     # subtle gold for highlights
HIGHLIGHT = RGBColor(0xD9,0x77,0x06) # orange for key data
BODY = RGBColor(0x37,0x41,0x51)     # dark grey body text
MUTED = RGBColor(0x9C,0xA3,0xAF)    # grey for footnotes/sources
CARD_BORDER = RGBColor(0xD1,0xD5,0xDB)
```

## Source Citation Format

Every slide ends with a footer bar:
```
add_shape(slide, 0, Inches(5.22), Inches(10), Inches(0.28), fill_color=RGBColor(0xF3,0xF4,0xF6))
add_text_box(slide, Inches(0.4), Inches(5.24), Inches(9.2), Inches(0.24),
             "信源：Source1；Source2；Source3", font_size=7, color=MUTED)
```

## Frameworks That Interviewers Expect

- **PEST**: Policy, Economy, Society, Technology — for macro scanning
- **Demand/Supply/Channel/Category**: For market growth drivers (e.g. makeup analysis)
- **MECE problem tree**: For market entry analysis
- **Competitor landscape**: Leader/Challenger/Niche positioning

## Performance Note

Complex PPTs with 50+ shapes can take 60-120s with python-pptx. Always run as background:
```python
terminal("python3 script.py", background=True, notify_on_complete=True, timeout=600)
```

## HTML Slide Fallback (When PPT Generation Times Out)

When `pptxgenjs` hangs (Node.js chart rendering timeout) AND `python-pptx` takes 120s+ with no output, use the **HTML slide fallback**:

1. Write an HTML file styled as a 960×540px slide (16:9 equivalent)
2. Open it via browser using `browser_navigate()` on `http://localhost:PORT/file.html`
3. Screenshot with `browser_vision()`
4. User pastes the screenshot into their PPT deck

Key sizes for HTML slide:
- Body: `display:flex; justify-content:center; align-items:center; min-height:100vh`
- Slide container: `width:960px; height:540px; background:#fafbfc; position:relative; overflow:hidden`
- Header: `height:68px; background:#1e3a5f; color:#fff`
- Footer: `height:26px; background:#f3f4f6`
- For manual bar charts, position bars with CSS `height` percentage and absolute positioning
- Use inline CSS `<style>` tag — no external dependencies

To serve the file, start a simple HTTP server in background:
```python
terminal("cd /path && python3 -m http.server PORT", background=True)
```
Then navigate browser to `http://localhost:PORT/filename.html`.

This is the FASTEST path to a visible deliverable when PPT generation is stuck. The HTML renders in milliseconds vs 120s+ for shape-heavy PPT.
