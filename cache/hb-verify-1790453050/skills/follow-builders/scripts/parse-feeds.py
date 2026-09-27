#!/usr/bin/env python3
"""Parse raw feed JSON files (feed-x.json, feed-podcasts.json, feed-blogs.json)
directly — no prepare-digest.js dependency. Use when the prepare script fails but
you've downloaded feeds via CDN mirrors or browser bypass.

Output: KEY=VALUE format (grep-friendly), same structure as parse-output.py.
"""
import json, sys

feeds = {}

# Load raw feed files
for name in ['x', 'podcasts', 'blogs']:
    path = f'/tmp/fb-feed-{name}.json'
    try:
        with open(path, 'r') as f:
            feeds[name] = json.load(f)
    except FileNotFoundError:
        print(f"WARNING: {path} not found", file=sys.stderr)
        feeds[name] = {}

# Stats
x_data = feeds.get('x', {})
p_data = feeds.get('podcasts', {})
b_data = feeds.get('blogs', {})

total_tweets = sum(len(b.get('tweets', [])) for b in x_data.get('x', []))
x_builders = len(x_data.get('x', []))
podcast_count = len(p_data.get('podcasts', []))
blog_count = len(b_data.get('blogs', []))

print(f"STATS_TOTAL_TWEETS={total_tweets}")
print(f"STATS_X_BUILDERS={x_builders}")
print(f"STATS_PODCASTS={podcast_count}")
print(f"STATS_BLOGS={blog_count}")

# X/Twitter builders
for bi, b in enumerate(x_data.get('x', [])):
    name = b.get('name', 'N/A')
    handle = b.get('handle', 'N/A')
    bio = b.get('bio', 'N/A')
    tweets = b.get('tweets', [])
    print(f"X_BUILDER_{bi}_NAME={name}")
    print(f"X_BUILDER_{bi}_HANDLE={handle}")
    print(f"X_BUILDER_{bi}_BIO={bio}")
    print(f"X_BUILDER_{bi}_TWEET_COUNT={len(tweets)}")
    for ti, t in enumerate(tweets):
        text = t.get('text', '').replace('\n', ' ').replace('\r', ' ')
        print(f"X_BUILDER_{bi}_TWEET_{ti}_DATE={t.get('date', '')}")
        print(f"X_BUILDER_{bi}_TWEET_{ti}_URL={t.get('url', '')}")
        print(f"X_BUILDER_{bi}_TWEET_{ti}_TEXT={text[:1000]}")

# Podcasts
for pi, p in enumerate(p_data.get('podcasts', [])):
    print(f"PODCAST_{pi}_NAME={p.get('name', p.get('source', 'N/A'))}")
    print(f"PODCAST_{pi}_TITLE={p.get('title', 'N/A')}")
    print(f"PODCAST_{pi}_URL={p.get('url', 'N/A')}")
    print(f"PODCAST_{pi}_DATE={p.get('date', 'N/A')}")
    print(f"PODCAST_{pi}_CHANNEL={p.get('channel', 'N/A')}")
    transcript = p.get('transcript', '')
    print(f"PODCAST_{pi}_TRANSCRIPT_LEN={len(transcript)}")
    for ci in range(0, min(len(transcript), 8000), 1000):
        chunk = transcript[ci:ci+1000].replace('\n', ' ').replace('\r', ' ')
        print(f"PODCAST_{pi}_TRANSCRIPT_{ci//1000}={chunk}")

# Blogs
for bi, blog in enumerate(b_data.get('blogs', [])):
    print(f"BLOG_{bi}_NAME={blog.get('name', 'N/A')}")
    print(f"BLOG_{bi}_TITLE={blog.get('title', 'N/A')}")
    print(f"BLOG_{bi}_URL={blog.get('url', 'N/A')}")

print("PARSE_COMPLETE=1")
