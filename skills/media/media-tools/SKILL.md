---
name: media-tools
description: "Media utility tools: GIF search via Tenor API and audio spectrograms via songsee."
version: 1.0.0
author: "Hermes Agent (curated from gif-search, songsee)"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [media, tools, gif, spectrogram, audio]
    related_skills: [youtube-content, spotify, heartmula, songwriting-and-ai-music]
---

# Media Tools

A collection of lightweight media utility tools. Each tool is self-contained and documented in its own reference file.

## When to Use

- User wants to search or download GIFs → **GIF Search** (`references/gif-search.md`)
- User wants audio spectrograms, mel features, chroma analysis → **songsee** (`references/songsee.md`)

## Tool Index

| Tool | Reference | Purpose |
|------|-----------|---------|
| GIF Search | `references/gif-search.md` | Search/download GIFs from Tenor API via curl |
| songsee | `references/songsee.md` | Audio spectrograms and multi-panel feature visualizations |

## General Workflow

1. Identify which tool the user needs based on their request
2. Load the specific reference: `skill_view(name="media-tools", file_path="references/<tool>.md")`
3. Follow the tool-specific instructions in the reference
4. Return results in the format the tool specifies

## Common Pitfalls

- **GIF Search** requires `TENOR_API_KEY` environment variable — set in `~/.hermes/.env`
- **songsee** requires Go toolchain (`go install github.com/steipete/songsee/cmd/songsee@latest`) and optionally `ffmpeg`
- These tools are bridge skills — they wrap CLI tools, not Hermes-native tools. Installation prerequisites must be met on the host.
