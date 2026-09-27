# CDN Fallback & Manual Feed Parsing Workflow

When `prepare-digest.js` fails with `fetch failed` but the CDN mirrors are reachable (DNS healthy, no proxy), use this complete manual workflow to download feeds and parse them directly.

## Diagnostic Check (confirm CDN is the path)

```bash
# Step 1: Check DNS — healthy means raw.githubusercontent.com resolves to real GitHub IPs
dig +short raw.githubusercontent.com
# HEALTHY: 185.199.108.133, 185.199.109.133, etc.
# POISONED: 198.18.0.x → use browser bypass instead (dns-poisoning-browser-bypass.md)

# Step 2: Test GitHub direct vs CDN
curl -sI --connect-timeout 10 https://raw.githubusercontent.com/zarazhangrui/follow-builders/main/feed-x.json
# TIMEOUT → GitHub blocked

curl -sI --connect-timeout 10 https://cdn.jsdelivr.net/gh/zarazhangrui/follow-builders@main/feed-x.json
# HTTP/2 200 → CDN works!
```

## Manual Feed Download

When GitHub is blocked but CDN works, download all three feeds:

```bash
curl -s --connect-timeout 15 -o /tmp/fb-feed-x.json \
  "https://cdn.jsdelivr.net/gh/zarazhangrui/follow-builders@main/feed-x.json"

curl -s --connect-timeout 15 -o /tmp/fb-feed-podcasts.json \
  "https://cdn.jsdelivr.net/gh/zarazhangrui/follow-builders@main/feed-podcasts.json"

curl -s --connect-timeout 15 -o /tmp/fb-feed-blogs.json \
  "https://cdn.jsdelivr.net/gh/zarazhangrui/follow-builders@main/feed-blogs.json"

# Verify all downloaded
wc -c /tmp/fb-feed-*.json
```

## Manual Feed Parsing

Use `scripts/parse-feeds.py` — it reads the raw feed JSON files directly (no prepare-digest.js dependency):

```bash
# In cron mode (execute_code blocked): write_file then terminal
# Copy parser and run
cp ~/.hermes/skills/follow-builders/scripts/parse-feeds.py /tmp/
python3 /tmp/parse-feeds.py > /tmp/fb-parsed.txt 2>&1

# Verify
grep 'STATS_' /tmp/fb-parsed.txt
grep 'PARSE_COMPLETE' /tmp/fb-parsed.txt
```

## Output Format

Same KEY=VALUE structure as `parse-output.py`:
- `STATS_TOTAL_TWEETS`, `STATS_X_BUILDERS`, `STATS_PODCASTS`, `STATS_BLOGS`
- `X_BUILDER_{i}_NAME/HANDLE/BIO/TWEET_COUNT`
- `X_BUILDER_{i}_TWEET_{j}_DATE/URL/TEXT`
- `PODCAST_{i}_NAME/TITLE/URL/TRANSCRIPT_LEN/TRANSCRIPT_{chunk}`
- `BLOG_{i}_NAME/TITLE/URL`
- `PARSE_COMPLETE=1`

## Feed JSON Structure

### feed-x.json
```json
{
  "generatedAt": "ISO timestamp",
  "lookbackHours": 336,
  "x": [
    {
      "name": "Swyx",
      "handle": "swyx",
      "bio": "...",
      "tweets": [
        {"date": "", "url": "https://x.com/...", "text": "..."}
      ]
    }
  ],
  "stats": {"totalTweets": 38, "xBuilders": 16}
}
```

### feed-podcasts.json
```json
{
  "generatedAt": "ISO timestamp",
  "lookbackHours": 336,
  "podcasts": [
    {
      "source": "podcast",
      "name": "The MAD Podcast with Matt Turck",
      "title": "Episode title",
      "url": "https://www.youtube.com/watch?v=...",
      "transcript": "Full transcript text (can be 80K+ chars)"
    }
  ],
  "stats": {"podcastEpisodes": 1}
}
```

### feed-blogs.json
```json
{
  "blogs": [
    {"name": "...", "title": "...", "url": "..."}
  ]
}
```

## Pitfalls

- **GitHub direct timeout ≠ DNS poisoning**: DNS resolves correctly but TCP connection times out. CDN mirrors are the correct fallback (not browser bypass).
- **Transcript size**: Podcast transcripts can be 80K+ characters. `parse-feeds.py` chunks them into 1000-char segments (up to 8 chunks) to avoid terminal output issues.
- **Empty blogs**: `feed-blogs.json` is often minimal (`{"blogs": []}`). That's normal — not all days have blog content.
