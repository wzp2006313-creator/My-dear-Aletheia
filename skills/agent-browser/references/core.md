---
name: core
description: Core agent-browser usage guide. Read this before running any agent-browser commands. Covers the snapshot-and-ref workflow, navigating pages, interacting with elements (click, fill, type, select), extracting text and data, taking screenshots, managing tabs, handling forms and auth, waiting for content, running multiple browser sessions in parallel, and troubleshooting common failures. Use when the user asks to interact with a website, fill a form, click something, extract data, take a screenshot, log into a site, test a web app, or automate any browser task.
allowed-tools: Bash(agent-browser:*), Bash(npx agent-browser:*)
---

# agent-browser core

Fast browser automation CLI for AI agents. Chrome/Chromium via CDP, no
Playwright or Puppeteer dependency. Accessibility-tree snapshots with compact
`@eN` refs let agents interact with pages in ~200-400 tokens instead of
parsing raw HTML.

Most normal web tasks (navigate, read, click, fill, extract, screenshot) are
covered here.

## The core loop

```bash
agent-browser open <url>        # 1. Open a page
agent-browser snapshot -i       # 2. See what's on it (interactive elements only)
agent-browser click @e3         # 3. Act on refs from the snapshot
agent-browser snapshot -i       # 4. Re-snapshot after any page change
```

Refs (`@e1`, `@e2`, ...) are assigned fresh on every snapshot. They become
**stale the moment the page changes**.

## Quickstart

```bash
# Install once
npm i -g agent-browser && agent-browser install

# Take a screenshot
agent-browser open https://example.com
agent-browser screenshot home.png
agent-browser close

# Search, click a result, and capture it
agent-browser open https://duckduckgo.com
agent-browser snapshot -i
agent-browser fill @e1 "agent-browser cli"
agent-browser press Enter
agent-browser wait --load networkidle
agent-browser snapshot -i
agent-browser click @e5
agent-browser screenshot result.png
```

## Reading a page

```bash
agent-browser snapshot                    # full tree
agent-browser snapshot -i                 # interactive elements only
agent-browser snapshot -i -u              # include href urls
agent-browser snapshot -i -c              # compact
agent-browser snapshot -i -d 3            # cap depth
agent-browser snapshot -s "#main"         # scope to CSS selector
agent-browser snapshot -i --json          # machine-readable
agent-browser get text @e1                # visible text
agent-browser get html @e1                # innerHTML
agent-browser get attr @e1 href           # attribute
agent-browser get title                   # page title
agent-browser get url                     # current URL
```

## Interacting

```bash
agent-browser click @e1                   # click
agent-browser click @e1 --new-tab         # open in new tab
agent-browser dblclick @e1                # double-click
agent-browser hover @e1                   # hover
agent-browser focus @e1                   # focus
agent-browser fill @e2 "hello"            # clear then type
agent-browser type @e2 " world"           # type without clearing
agent-browser press Enter                 # key press
agent-browser check @e3                   # check checkbox
agent-browser select @e4 "option-value"   # select dropdown
agent-browser upload @e5 file1.pdf        # upload file(s)
agent-browser scroll down 500             # scroll
agent-browser scrollintoview @e1          # scroll into view
agent-browser drag @e1 @e2                # drag and drop
```

### Semantic locators (no snapshot needed)

```bash
agent-browser find role button click --name "Submit"
agent-browser find text "Sign In" click
agent-browser find label "Email" fill "user@test.com"
agent-browser find placeholder "Search" type "query"
agent-browser find testid "submit-btn" click
agent-browser find first ".card" click
agent-browser find nth 2 ".card" hover
```

### Raw CSS fallback

```bash
agent-browser click "#submit"
agent-browser fill "input[name=email]" "user@test.com"
```

## Waiting

```bash
agent-browser wait @e1                     # until element appears
agent-browser wait --text "Success"        # until text appears
agent-browser wait --url "**/dashboard"    # until URL matches
agent-browser wait --load networkidle      # until network idle
agent-browser wait --load domcontentloaded
agent-browser wait --fn "window.ready"     # JS condition
```

## Common workflows

### Log in

```bash
agent-browser open https://app.example.com/login
agent-browser snapshot -i
agent-browser fill @e3 "user@example.com"
agent-browser fill @e4 "hunter2"
agent-browser click @e5
agent-browser wait --url "**/dashboard"
agent-browser snapshot -i
```

### Persist session

```bash
agent-browser state save ./auth.json
agent-browser --state ./auth.json open https://app.example.com
# Or: AGENT_BROWSER_SESSION_NAME=my-app agent-browser open ...
```

### Extract data

```bash
agent-browser snapshot -i --json > page.json
cat <<'EOF' | agent-browser eval --stdin
const rows = document.querySelectorAll("table tbody tr");
Array.from(rows).map(r => ({
  name: r.cells[0].innerText,
  price: r.cells[1].innerText,
}));
EOF
```

### Screenshot

```bash
agent-browser screenshot                        # temp path
agent-browser screenshot page.png               # specific path
agent-browser screenshot --full full.png        # full scroll height
agent-browser screenshot --annotate map.png     # numbered labels + legend
```

### Handle multiple tabs

```bash
agent-browser tab                      # list tabs
agent-browser tab new https://docs...  # open new tab
agent-browser tab 2                    # switch to tab 2
agent-browser tab close 2              # close tab 2
```

### Run multiple browsers in parallel

```bash
agent-browser --session a open https://app.example.com
agent-browser --session b open https://app.example.com
```

### Network mocking

```bash
agent-browser network route "**/api/users" --body '{"users":[]}'
agent-browser network route "**/analytics" --abort
agent-browser network requests
agent-browser network har start
agent-browser network har stop /tmp/trace.har
```

### Record video

```bash
agent-browser record start demo.webm
agent-browser open https://example.com
agent-browser record stop
```

## Diagnosing install issues

```bash
agent-browser doctor                     # full diagnosis
agent-browser doctor --fix               # also run repairs
```

## React introspection

```bash
agent-browser open --enable react-devtools http://localhost:3000
agent-browser react tree                         # component tree
agent-browser react renders start/stop            # render profile
agent-browser vitals [url]                        # LCP/CLS/TTFB/FCP/INP
agent-browser pushstate <url>                     # SPA navigation
```