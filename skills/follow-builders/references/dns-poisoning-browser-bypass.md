# Bypassing DNS Poisoning with Browser Tool

When `raw.githubusercontent.com` resolves to `198.18.0.x` (IETF TEST-NET-2, DNS poisoning) and all CDN mirrors fail, the browser tool can often bypass the restriction because it uses its own network stack with independent DNS resolution.

## Approach A: `agent-browser` CLI (preferred — works in cron + interactive)

The `agent-browser` CLI launches a real Chrome/Chromium via CDP with its own DNS stack. It's installed as part of Hermes Agent and works in both cron and interactive sessions.

```bash
# Verify it's installed
which agent-browser && agent-browser --version

# Fetch each feed
agent-browser open "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json"
agent-browser wait --load networkidle
agent-browser get text > /tmp/fb-feed-x.json

agent-browser open "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-podcasts.json"
agent-browser wait --load networkidle
agent-browser get text > /tmp/fb-feed-podcasts.json

agent-browser open "https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-blogs.json"
agent-browser wait --load networkidle
agent-browser get text > /tmp/fb-feed-blogs.json

agent-browser close
```

If `agent-browser` fails with `ERR_TUNNEL_CONNECTION_FAILURE`, this confirms **TCP-level blocking** (not just DNS poisoning) — skip to "When it doesn't work" below.

## Approach B: Browser tools via delegate_task (interactive sessions only)

In interactive sessions with browser tools available, use `browser_navigate` + `browser_console`:

### 1. Navigate to the feed JSON directly
```
browser_navigate → https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json
```

### 2. Extract the JSON from the page
```
browser_console → document.body.innerText
```
The page is plain JSON — `innerText` returns the full raw content. Parse the `result` field as JSON.

**⚠️ Cron mode limitation**: `browser_navigate` / `browser_console` tools are typically not available in cron sessions. Use Approach A (`agent-browser` CLI) in cron mode instead.

**⚠️ delegate_task pitfall**: Spawning a subagent with `toolsets=["browser"]` or `toolsets=["web"]` does NOT guarantee actual HTTP/browser capabilities — the subagent may only have shell access. `agent-browser` CLI (Approach A) is more reliable because it's a local binary with its own CDP transport.

### 3. Repeat for all three feeds
- `feed-x.json` — X/Twitter posts from builders
- `feed-podcasts.json` — podcast transcripts  
- `feed-blogs.json` — blog post content

### 4. Parse and remix manually
Since `prepare-digest.js` can't run (it fetches from the same poisoned DNS), parse the browser-extracted JSON manually:

**feed-x.json structure:**
```json
{
  "generatedAt": "...",
  "x": [
    {
      "source": "x",
      "name": "Builder Name",
      "handle": "handle",
      "bio": "...",
      "tweets": [
        {
          "id": "...",
          "text": "...",
          "url": "https://x.com/handle/status/...",
          "likes": N,
          "retweets": N,
          "replies": N,
          "isQuote": true/false,
          "quotedTweetId": "..."
        }
      ]
    }
  ],
  "stats": { "xBuilders": N, "totalTweets": N }
}
```

**feed-podcasts.json structure:**
```json
{
  "podcasts": [
    {
      "source": "podcast",
      "name": "Podcast Name",
      "title": "Episode Title",
      "url": "https://www.youtube.com/watch?v=...",
      "publishedAt": "...",
      "transcript": "Speaker 1 | ..."
    }
  ],
  "stats": { "podcastEpisodes": N }
}
```

**feed-blogs.json structure:**
```json
{
  "blogs": [
    {
      "source": "blog",
      "name": "Blog Name",
      "title": "Post Title",
      "url": "...",
      "publishedAt": "...",
      "content": "..."
    }
  ],
  "stats": { "blogPosts": N }
}
```

### 5. Remix following the same rules
- NEVER invent content — only use data from the extracted JSON
- Every item MUST have its URL
- Use the `config.language` preference from `~/.follow-builders/config.json`
- Follow the 4-chapter digest structure

## Why this works

The browser tool runs in a hosted browser environment (Browserbase) which uses its own DNS resolvers — typically Google Public DNS or Cloudflare — rather than the local network's resolver. This means it bypasses corporate/ISP-level DNS poisoning that targets `raw.githubusercontent.com`.

## When it doesn't work

If the browser tool also fails to reach `raw.githubusercontent.com`, it's a full network restriction (not just DNS). In that case, the only option is to configure a VPN/proxy or wait for the restriction to be lifted.
