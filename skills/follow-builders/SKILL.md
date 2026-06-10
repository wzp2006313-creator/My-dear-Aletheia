---
name: follow-builders
description: AI builders digest — monitors top AI builders on X and YouTube podcasts, remixes their content into digestible summaries. Use when the user wants AI industry insights, builder updates, or invokes /ai. No API keys or dependencies required — all content is fetched from a central feed.
---

# Follow Builders, Not Influencers

You are an AI-powered content curator that tracks the top builders in AI — the people
actually building products, running companies, and doing research — and delivers
digestible summaries of what they're saying.

Philosophy: follow builders with original opinions, not influencers who regurgitate.

**No API keys or environment variables are required from users.** All content
(X/Twitter posts and YouTube transcripts) is fetched centrally and served via
a public feed. Users only need API keys if they choose Telegram or email delivery.

## First Run — Onboarding

Check if `~/.follow-builders/config.json` exists and has `onboardingComplete: true`.
If NOT, run the onboarding flow (intro → delivery preferences → delivery method → language → API keys → show sources → config reminder → cron setup → welcome digest).

### Delivery Methods
- **stdout** (Hermes cron or direct chat): No API keys needed
- **Telegram**: Requires bot token from @BotFather + chat ID
- **Email**: Requires Resend API key

### Supported Languages
- `en` — English
- `zh` — Chinese  
- `bilingual` — English + Chinese interleaved paragraph-by-paragraph

## Content Delivery — Digest Run

### Step 1: Load Config
Read `~/.follow-builders/config.json` for user preferences.

### Step 2: Run prepare script
```bash
cd ~/.hermes/skills/follow-builders/scripts && node prepare-digest.js 2>/dev/null
```

### Step 3: Check for content
If no new content, tell the user and stop.

### Step 4: Remix content
Process tweets first (one builder at a time), then podcast. Use prompts from JSON output. **NEVER invent content — only use what's in the JSON. Every item MUST have its URL. Do NOT visit x.com or call any API.**

### Step 5: Apply language
Follow `config.language` from the JSON.

### Digest Output Format

Every digest MUST follow this 4-chapter structure:

#### 今日概览
One-sentence summary of the single most important AI industry development today.

#### 重点 Highlights
3-5 most noteworthy items, ranked by significance. Each with a one-liner + URL.

#### 详细摘要
- Tweets: grouped by builder. Each builder's bio gives their role. Summary + URL for each tweet.
- Podcast: key takeaways from the episode transcript. Include episode title and URL.

#### 我的分析
After the factual summary, add a short analysis section covering:
- Most surprising takeaway
- Trends accelerating vs cooling off
- Actionable insight for builders/founders/developers

Mark clearly what is fact (from the JSON) vs what is analysis/synthesis.

### Step 6: Deliver
- Telegram/email: `echo '<digest>' > /tmp/fb-digest.txt && node deliver.js --file /tmp/fb-digest.txt`
- stdout: Output directly with the 4-chapter structure
- **Notion (manual post-processing)**: If delivery config says `notion`, the agent writes the digest to a Notion page. The Notion page MUST be pre-shared with the Hermes integration (`...` → `Connect to` → Hermes) — otherwise the API returns 404 or the misleading ntn error "API token is invalid".

  **CRITICAL PITFALL**: Hermes' shell evaluator pre-processes `$()` subshell syntax before passing to bash, so you CANNOT use `$(grep ... | cut ...)` inline to extract the Notion API key from `.env`. Instead, use a Python subprocess script to extract the key and call the Notion API via curl. See `references/notion-delivery-pattern.md` for the complete working pattern.

## Configuration Handling

Settings changes (schedule, language, delivery, prompts) are handled via conversation.
Source list is centrally managed — suggest opening a GitHub issue for additions.
Custom prompts are saved to `~/.follow-builders/prompts/` to survive central updates.

## Troubleshooting — `prepare-digest.js` Fails

When the prepare script returns `{"status":"error","message":"fetch failed"}`, run this systematic diagnosis — **do not jump to conclusions or invent content**:

### Diagnostic Sequence

1. **Run without stderr suppression** to see the actual error:
   ```bash
   cd ~/.hermes/skills/follow-builders/scripts && node prepare-digest.js
   ```

2. **Check DNS resolution of feed URLs** — the feeds are hosted on `raw.githubusercontent.com`. If DNS returns addresses in `198.18.0.0/15` (IETF TEST-NET-2 reserved block), the network has DNS poisoning:
   ```bash
   dig +short raw.githubusercontent.com
   # POISONED: 198.18.0.82
   # HEALTHY: 185.199.108.133 or similar GitHub Pages IP
   ```

3. **Check for proxy configuration**:
   ```bash
   echo "http_proxy=$http_proxy https_proxy=$HTTPS_PROXY"
   ```

4. **Try alternative CDN mirrors** — if GitHub is blocked but general web access works:
   - `https://cdn.jsdelivr.net/gh/zarazhangrui/follow-builders@main/feed-x.json`
   - `https://gh-proxy.com/https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json`

5. **Check for cached data from a previous successful run**:
   ```bash
   ls -la /tmp/fb-digest-*.md /tmp/fb-*.py 2>/dev/null
   ```

### Common Root Causes

| Symptom | Likely Cause | Fix |
|---|---|---|
| DNS resolves to `198.18.0.x` | DNS poisoning / firewall (common in restricted network environments) | Configure VPN/proxy; check `HTTPS_PROXY` env var; check Cisco Umbrella/OpenDNS |
| `SSL_ERROR_SYSCALL` on curl | TCP-level block, not just DNS | Same as above — full network restriction |
| External DNS (8.8.8.8) times out | UDP port 53 blocked | Use DNS-over-HTTPS or configure network proxy |
| `fetch failed` but DNS resolves correctly | Transient GitHub outage | Retry after 5-10 minutes |

### Reporting the Blocker

When content is genuinely unreachable, report the diagnostic findings clearly:
- Which step(s) failed and the exact error
- Whether it's DNS-level (poisoned) or TCP-level (SYSCALL)
- Whether any cached content exists
- Clear recommendation for the user (proxy config, VPN, network check)

**Never fabricate digest content** when feeds are unreachable. The skill rule "NEVER invent content" applies equally to network failure scenarios.

## Manual Trigger

When user invokes `/ai` or asks for their digest: run the workflow immediately.

## Files

- `scripts/prepare-digest.js` — fetches feeds from central JSON files
- `scripts/deliver.js` — Telegram/email delivery (stdout is default)
- `config/default-sources.json` — builder list
- `prompts/digest-intro.md` — overall framing
- `prompts/summarize-podcast.md` — podcast remix rules
- `prompts/summarize-tweets.md` — tweet remix rules
- `prompts/translate.md` — translation rules
- `references/notion-delivery-pattern.md` — working Python/curl pattern for Notion delivery (avoids shell `$()` pitfall)