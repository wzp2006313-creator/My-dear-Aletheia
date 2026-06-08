---
name: github-workflows
description: "Complete GitHub interaction workflows: auth, repos, PRs, issues, code review, CI, releases, and codebase inspection. Use when working with GitHub in any capacity — cloning, branching, PR lifecycle, issue triage, code review, CI monitoring, repo management, or codebase analysis."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, git, PR, issues, code-review, CI, repos, auth, codebase, workflow]
    related_skills: [hermes-agent]
---

# GitHub Workflows

Complete guide for interacting with GitHub — authentication, repository management, pull requests, issues, code review, CI/CD, and codebase inspection. All sections support both `gh` CLI and `git` + `curl` fallbacks, so no `gh` installation is required.

## Quick Start: Auth Detection

Before any GitHub operation, detect the auth method:

```bash
# Load auth helpers
source "${HERMES_HOME:-$HOME/.hermes}/skills/github/github-workflows/scripts/gh-env.sh"

# Or inline:
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if [ -f ~/.hermes/.env ] && grep -q "^GITHUB_TOKEN=" ~/.hermes/.env; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" ~/.hermes/.env | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\1|')
    fi
  fi
fi
```

## Facet Index

This umbrella covers six facets of GitHub interaction. Each has a corresponding reference file with full command details, `gh` vs `curl` alternatives, and troubleshooting:

| Facet | Reference | Key Operations |
|-------|-----------|---------------|
| **Authentication** | [references/auth.md](references/auth.md) | HTTPS tokens, SSH keys, gh login, credential helpers |
| **Repository Management** | [references/repo-management.md](references/repo-management.md) | Clone, create, fork, releases, secrets, CI workflows |
| **Pull Request Workflow** | [references/pr-workflow.md](references/pr-workflow.md) | Branch, commit, push, create PR, CI polling, auto-fix, merge |
| **Code Review** | [references/code-review.md](references/code-review.md) | Pre-push review, PR review, inline comments, formal review submission |
| **Issue Management** | [references/issues.md](references/issues.md) | Create, search, triage, label, assign, close, bulk operations |
| **Codebase Inspection** | [references/codebase-inspection.md](references/codebase-inspection.md) | LOC counts, language breakdown, code-vs-comment ratios via pygount |

## Templates

- [PR body (feature)](templates/pr-body-feature.md) — feature PR description template
- [PR body (bugfix)](templates/pr-body-bugfix.md) — bugfix PR description template
- [Bug report](templates/bug-report.md) — GitHub issue bug report template
- [Feature request](templates/feature-request.md) — GitHub issue feature request template

## Workflow Recipes

### Recipe: Quick fix → PR → merge

```bash
# 1. Branch
git checkout main && git pull origin main
git checkout -b fix/description

# 2. Make changes (use file tools), then commit
git add <files>
git commit -m "fix: description"

# 3. Push and create PR
git push -u origin HEAD
gh pr create --title "fix: description" --body "## Summary\n..."
# Or with curl: POST /repos/$OWNER/$REPO/pulls

# 4. Monitor CI
gh pr checks --watch
# Or: curl GET /repos/$OWNER/$REPO/commits/$SHA/status

# 5. Merge when green
gh pr merge --squash --delete-branch
```

### Recipe: Review a PR

```bash
# 1. Fetch and check out
git fetch origin pull/$PR_NUMBER/head:pr-$PR_NUMBER
git checkout pr-$PR_NUMBER

# 2. Review the diff
git diff main...HEAD --stat
git diff main...HEAD

# 3. Post review
gh pr review $PR_NUMBER --approve --body "LGTM"
# Or with curl: POST /repos/$OWNER/$REPO/pulls/$PR_NUMBER/reviews

# 4. Clean up
git checkout main && git branch -D pr-$PR_NUMBER
```

### Recipe: Triage issues

```bash
# List untriaged
gh issue list --label "needs-triage" --state open

# Apply labels and assign
gh issue edit 42 --add-label "priority:high,bug"
gh issue edit 42 --add-assignee @me
```

### Recipe: Create a release

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
# Or with curl: POST /repos/$OWNER/$REPO/releases
```

### Recipe: Codebase analysis

```bash
pip install pygount
cd /path/to/repo
pygount --format=summary \
  --folders-to-skip=".git,node_modules,venv,.venv,__pycache__,.cache,dist,build" \
  .
```

## Common Pitfalls

1. **Fine-grained PATs need Contents: Read and write explicitly** — `permissions.push=true` is not sufficient for actual git push. Always verify with `git ls-remote` after setup.
2. **Secret redaction eats fine-grained tokens** — Hermes security scanning auto-redacts fine-grained PATs when written via `write_file`/`patch`. Use `git credential-store` directly in the terminal, or prefer classic tokens / SSH keys for automated workflows.
3. **gh not installed ≠ blocked** — every operation has a `curl` fallback. Use the auth detection block to route automatically.
4. **Always exclude .git, node_modules, venv from pygount** — without `--folders-to-skip`, pygount crawls dependency trees and may hang.
5. **CI polling without watch** — when `gh pr checks --watch` isn't available, use the polling loop in `references/ci-troubleshooting.md`.
6. **Squash merge deletes branch** — the `--delete-branch` flag is safe; the commits remain in the squash commit on main.
