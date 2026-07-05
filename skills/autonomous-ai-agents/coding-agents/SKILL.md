---
name: coding-agents
description: "Delegate coding tasks to external AI coding agents (Claude Code, Codex, OpenCode) via Hermes terminal — features, refactoring, PR reviews, parallel batch work. Use when the user wants to delegate implementation to a standalone coding agent."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Coding-Agent, Claude, Codex, OpenCode, delegate, refactoring, PR-review, automation, PTY]
    related_skills: [hermes-agent, kanban-orchestrator]
---

# Coding Agents

Delegate coding tasks to external AI coding agent CLIs from within Hermes. Three tools are supported, each with its own reference file for full CLI details:

| Agent | CLI | Auth | Reference |
|-------|-----|------|-----------|
| **Claude Code** | `claude` (npm) | OAuth or `ANTHROPIC_API_KEY` | [references/claude-code.md](references/claude-code.md) |
| **Codex** | `codex` (npm) | OAuth or `OPENAI_API_KEY` | [references/codex.md](references/codex.md) |
| **OpenCode** | `opencode` (npm/brew) | `opencode auth login` or provider keys | [references/opencode.md](references/opencode.md) |

## Common Patterns (All Agents)

### Pattern 1: One-Shot Task
For bounded tasks that should run and exit:
```bash
# Claude Code (preferred — print mode, no PTY needed)
terminal(command="claude -p 'Add retry logic to API calls' --max-turns 10", workdir="~/project", timeout=180)
# Codex
terminal(command="codex exec 'Add retry logic to API calls'", workdir="~/project", pty=true)
# OpenCode
terminal(command="opencode run 'Add retry logic to API calls'", workdir="~/project")
```

### Pattern 2: Background Long-Running Task
For tasks needing monitoring or iteration:
```bash
terminal(command="claude -p 'Refactor auth module' --max-turns 20", workdir="~/project", background=true, notify_on_complete=True)
# Monitor: process(action="poll"/"log"/"wait")
```

### Pattern 3: PR Review
```bash
# Quick review of diff vs main
cd ~/project && git diff main...HEAD | claude -p 'Review this diff for bugs, security issues, and style' --max-turns 1
# Or: codex exec, opencode run with git diff piped
```

### Pattern 4: Parallel Work (Isolated Worktrees)
```bash
git worktree add -b fix/issue-101 /tmp/issue-101 main
git worktree add -b fix/issue-102 /tmp/issue-102 main
terminal(command="claude -p 'Fix issue #101' --max-turns 15", workdir="/tmp/issue-101", background=true, notify_on_complete=True)
terminal(command="claude -p 'Fix issue #102' --max-turns 15", workdir="/tmp/issue-102", background=true, notify_on_complete=True)
```

## Agent Selection Guide

| Task | Best Agent | Why |
|------|-----------|-----|
| Complex multi-step features | Claude Code or Codex | Best reasoning and code generation |
| Quick bug fixes | Any | All three handle simple fixes well |
| PR reviews | Claude Code | Pipe diff, `--max-turns 1`, structured output |
| Batch parallel work | Any | All support isolated worktrees |
| Interactive multi-turn | Claude Code (tmux) | Best TUI for iterative work |
| Cost-sensitive work | OpenCode | Provider-agnostic, choose cheapest model |
| CI/automation | Claude Code (`--bare`) | Fast startup, no OAuth needed |

## Shared Pitfalls

1. **Git repo required** — Codex and OpenCode won't run outside a git repo. Claude Code works anywhere but is safer in one. For scratch work: `mktemp -d && git init`.
2. **PTY for interactive mode** — all three need `pty=true` for interactive/TUI sessions. Print mode (`claude -p`, `opencode run`) doesn't need PTY.
3. **Isolate worktrees for parallel runs** — never share a working directory across parallel agent processes.
4. **Set `--max-turns` or timeout** — prevents runaway costs in print mode.
5. **Clean up tmux sessions and worktrees** — `tmux kill-session`, `git worktree remove` when done.
6. **Background + notify_on_complete** — for long tasks, always use `notify_on_complete=true` so you know when the agent finishes.
