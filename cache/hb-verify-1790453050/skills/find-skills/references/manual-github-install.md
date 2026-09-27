# Manual GitHub Install — Skills Outside the npx Registry

Use this workflow when the user asks to install skills from a GitHub repository that isn't registered on the `npx skills` registry (or for repos where `npx skills add` would pull a stub rather than a complete package).

## Overview

Three phases: **Discover** → **Fetch** → **Install**

---

## Phase 1: Discover Skills in a Repository

### 1a. List skills directories

Use the browser or `curl` + GitHub API (authenticated tokens only — unauthenticated API calls hit rate limits fast). When API limits block you, use the browser:

```bash
# Browser: navigate to repo root and look at the file tree
browser_navigate(url="https://github.com/<owner>/<repo>")
# Look for directories named 'skills/', or top-level directories that contain a skills/ subdirectory
# Common structures:
#   repo/skills/<skill-name>/SKILL.md          ← flat
#   repo/<domain>/skills/<skill-name>/SKILL.md ← domain-grouped
#   repo/.github/skills/<skill-name>/SKILL.md  ← microsoft convention
```

### 1b. Identify which module directories have SKILL.md files

Each skill is a directory containing a `SKILL.md` file. Navigate into the `skills/` directory to list them:

```bash
browser_navigate(url="https://github.com/<owner>/<repo>/tree/main/skills")
# Read the file tree — each subdirectory is a skill name
```

### 1c. Verify quality before proceeding

| Signal | What to check |
|--------|--------------|
| GitHub stars | Repos with <100 stars: be cautious |
| Commit recency | Not updated in 6+ months: may be stale |
| SKILL.md presence | A directory without SKILL.md is not a skill |
| Description quality | Vague 1-line descriptions may indicate low effort |

---

## Phase 2: Fetch SKILL.md Content

### Raw URL construction

The raw URL pattern for GitHub is:

```
https://raw.githubusercontent.com/<owner>/<repo>/<branch>/<path-to-skill>/SKILL.md
```

Examples from this session:

| Repo | Pattern |
|------|---------|
| anthropics/skills (flat) | `https://raw.githubusercontent.com/anthropics/skills/main/skills/<name>/SKILL.md` |
| microsoft/skills | `https://raw.githubusercontent.com/microsoft/skills/main/.github/skills/<name>/SKILL.md` |
| eze-is/web-access | `https://raw.githubusercontent.com/eze-is/web-access/main/SKILL.md` |
| vercel-labs/agent-browser | `https://raw.githubusercontent.com/vercel-labs/agent-browser/main/skills/agent-browser/SKILL.md` |
| op7418/guizang-ppt-skill | `https://raw.githubusercontent.com/op7418/guizang-ppt-skill/main/SKILL.md` |
| NBreeze-Eric/financial-services (nested) | `https://raw.githubusercontent.com/<owner>/<repo>/main/<domain>/skills/<name>/SKILL.md` |

### Fetch

```bash
curl -sL "https://raw.githubusercontent.com/<owner>/<repo>/main/<path>/SKILL.md"
```

**Common issues:**
- Content may lack YAML frontmatter (`---`). If `skill_manage` fails with "Frontmatter missing", prepend a `---\nname: <skill-name>\ndescription: <desc>\n---\n` header.
- Rate-limited API calls: switch to browser instead of curl.
- Raw content over ~50KB: the `create` action still accepts it as the `content` parameter.

---

## Phase 3: Install via skill_manage

### Single skill

```python
skill_manage(
    action="create",
    name="<skill-name>",
    content="<full SKILL.md content>"
)
```

### Batch install (many skills from one repo)

**DO NOT** install skills one at a time in series for repos with 5+ skills. Always use `delegate_task` with parallel tasks (max 3 concurrent children per batch):

```python
delegate_task(
    tasks=[
        {"goal": "Install <skill-A>", "context": "curl URL_A; skill_manage create", "toolsets": ["terminal","skills"]},
        {"goal": "Install <skill-B>", "context": "curl URL_B; skill_manage create", "toolsets": ["terminal","skills"]},
        {"goal": "Install <skill-C>", "context": "curl URL_C; skill_manage create", "toolsets": ["terminal","skills"]},
    ]
)
```

Batch after batch, tracking progress with `todo`:

```
todo(merge=true, todos=[{id: "batch-1", status: "completed"}, ...])
```

### Handling missing frontmatter

Some GitHub repos store bare markdown without YAML frontmatter. If `skill_manage(action="create")` returns a frontmatter error:

1. Prepend `---\nname: <skill-name>\ndescription: <one-line description>\n---\n` to the fetched content
2. Retry the `skill_manage(action="create")` call
3. If description isn't obvious from content, use the first paragraph or heading as description

### After install

Verify with `skill_view(name)` to confirm `readiness_status: "available"`.

---

## Phase 4: Multi-Source Discovery

When the user asks "what must-have skills am I missing?", check all major skill repositories:

1. **vercel-labs/skills** — Original ecosystem. Usually contains `find-skills` only.
2. **anthropics/skills** — Largest collection (~17 skills). 145K stars. The highest-quality source.
3. **microsoft/skills** — Azure/Microsoft ecosystem. ~19 skills.
4. **Individual repos** — Community authors (eze-is, op7418, PleasePrompto, etc.)

Compare against the current installed skills list (`skills_list()`), then recommend from the gap.

---

## Known Repositories Reference

| Repository | Stars | Skills Count | URL Pattern |
|-----------|-------|-------------|-------------|
| anthropics/skills | 145K | ~17 | `skills/<name>/SKILL.md` |
| vercel-labs/skills | 20.9K | 1 (find-skills) | `skills/<name>/SKILL.md` |
| microsoft/skills | 2.4K | ~19 | `.github/skills/<name>/SKILL.md` |
| eze-is/web-access | — | 1 | root `SKILL.md` |
| op7418/guizang-ppt-skill | — | 1 | root `SKILL.md` |
| vercel-labs/agent-browser | — | 1 (stub) | `skills/agent-browser/SKILL.md` |
| PleasePrompto/notebooklm-skill | — | 1 | root `SKILL.md` |
