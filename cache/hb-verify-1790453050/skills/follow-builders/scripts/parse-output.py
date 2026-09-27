#!/usr/bin/env python3
"""Parse prepare-digest.js JSON output into structured KEY=VALUE format.
Use this in cron mode (where execute_code is blocked) — write with write_file, run with terminal().
Output is designed for grep: grep '^STATS_' for counts, grep '^X_BUILDER_' for tweets, etc."""

import json, sys

with open('/tmp/fb-digest-raw.json', 'r') as f:
    data = json.load(f)

stats = data.get('stats', {})
cf = data.get('config', {})

# Status & stats
print(f"STATUS={data.get('status', 'N/A')}")
print(f"STATS_TOTAL_TWEETS={stats.get('totalTweets', 0)}")
print(f"STATS_X_BUILDERS={stats.get('xBuilders', 0)}")
print(f"STATS_PODCAST_EPISODES={stats.get('podcastEpisodes', 0)}")
print(f"STATS_BLOG_POSTS={stats.get('blogPosts', 0)}")
print(f"CONFIG_LANGUAGE={cf.get('language', 'N/A')}")

# Podcasts
for idx, p in enumerate(data.get('podcasts', [])):
    print(f"PODCAST_{idx}_TITLE={p.get('title', 'N/A')}")
    print(f"PODCAST_{idx}_URL={p.get('url', 'N/A')}")
    print(f"PODCAST_{idx}_DATE={p.get('date', 'N/A')}")
    print(f"PODCAST_{idx}_CHANNEL={p.get('channel', 'N/A')}")
    transcript = p.get('transcript', '')
    print(f"PODCAST_{idx}_TRANSCRIPT_LEN={len(transcript)}")
    print(f"PODCAST_{idx}_TRANSCRIPT_PREVIEW={transcript[:500].replace(chr(10), ' ')}")

# X/Twitter builders (key is 'x', not 'builders')
for bi, b in enumerate(data.get('x', [])):
    print(f"X_BUILDER_{bi}_NAME={b.get('name', 'N/A')}")
    print(f"X_BUILDER_{bi}_HANDLE={b.get('handle', 'N/A')}")
    print(f"X_BUILDER_{bi}_BIO={b.get('bio', 'N/A')}")
    tweets = b.get('tweets', [])
    print(f"X_BUILDER_{bi}_TWEET_COUNT={len(tweets)}")
    for ti, t in enumerate(tweets):
        text = t.get('text', '').replace('\n', ' ')
        print(f"X_BUILDER_{bi}_TWEET_{ti}_DATE={t.get('date', '')}")
        print(f"X_BUILDER_{bi}_TWEET_{ti}_URL={t.get('url', '')}")
        print(f"X_BUILDER_{bi}_TWEET_{ti}_TEXT={text}")

# Blogs
for bi, blog in enumerate(data.get('blogs', [])):
    print(f"BLOG_{bi}_NAME={blog.get('name', 'N/A')}")
    print(f"BLOG_{bi}_TITLE={blog.get('title', 'N/A')}")
    print(f"BLOG_{bi}_URL={blog.get('url', 'N/A')}")

print("PARSE_COMPLETE=1")
