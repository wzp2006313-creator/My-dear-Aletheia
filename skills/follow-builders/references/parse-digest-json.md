# Parsing prepare-digest.js Output

> **Quick start**: Copy `scripts/parse-output.py` to `/tmp/` and run it. It outputs all tweets, podcasts, and stats in grep-friendly `KEY=VALUE` format. Use the patterns below only if you need a custom parser.

The `prepare-digest.js` script outputs a JSON object with this structure:

```json
{
  "status": "ok",
  "generatedAt": "ISO timestamp",
  "config": { "language": "zh", ... },
  "podcasts": [{ "name": "...", "title": "...", "url": "...", "transcript": "..." }],
  "x": [{ "name": "...", "handle": "...", "bio": "...", "tweets": [{ "text": "...", "url": "...", "created_at": "..." }] }],
  "blogs": [{ "name": "...", "title": "...", "url": "...", "content": "..." }],
  "stats": { "podcastEpisodes": N, "xBuilders": N, "totalTweets": N, "blogPosts": N },
  "prompts": { "summarize_podcast": "...", "summarize_tweets": "...", "summarize_blogs": "..." }
}
```

## Quick Parse Script (cron-safe)

In cron mode, `execute_code` is blocked — write a script with `write_file`, then run with `terminal()`:

```python
#!/usr/bin/env python3
import json

with open('/tmp/fb-digest-raw.json') as f:
    data = json.load(f)

# Check if there's content
if data.get('status') != 'ok':
    print("NO_CONTENT")
    exit()

stats = data.get('stats', {})
print(f"Podcasts: {stats.get('podcastEpisodes', 0)}")
print(f"Builders: {stats.get('xBuilders', 0)}")
print(f"Tweets: {stats.get('totalTweets', 0)}")
print(f"Blogs: {stats.get('blogPosts', 0)}")

# Extract tweets
for builder in data.get('x', []):
    name = builder.get('name')
    handle = builder.get('handle')
    bio = builder.get('bio')
    for tweet in builder.get('tweets', []):
        print(f"\n[{name} @{handle}] {tweet.get('text', '')[:200]}")
        print(f"  URL: {tweet.get('url')}")

# Extract podcasts
for pod in data.get('podcasts', []):
    print(f"\n[Podcast: {pod.get('name')}] {pod.get('title')}")
    print(f"  URL: {pod.get('url')}")
    print(f"  Transcript: {len(pod.get('transcript', ''))} chars")

# Extract blogs
for blog in data.get('blogs', []):
    print(f"\n[Blog: {blog.get('name')}] {blog.get('title')}")
    print(f"  URL: {blog.get('url')}")
    print(f"  Content: {len(blog.get('content', ''))} chars")
```

## Filtering Non-Substantive Tweets

The feed includes all tweets from tracked builders. For the digest, skip:
- Humor/meme tweets with no AI insight (e.g., "Some people meditate, I listen to @EITS")
- Pure promotion without substance (e.g., "Vibecon recap" with no details)
- Team announcements without broader context (e.g., "Blessed to have him on the team")
- Engagement bait / "@ mention spam" (e.g., long lists of @mentions)

Keep: original opinions, product announcements, technical discussions, industry analysis, contrarian takes, and practical tips.
