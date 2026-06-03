#!/bin/bash
# Hermes Agent daily backup to GitHub
# Runs via cron, pushes ~/.hermes/ config, skills, cron, scripts etc.
# Excludes: .env, venv/, node_modules/, __pycache__/, .git/

set -euo pipefail

BACKUP_DIR="/tmp/hermes-backup-$(date +%Y%m%d)"
REPO_DIR="$HOME/.hermes"
REMOTE="git@github.com:wzp2006313-creator/My-dear-Aletheia.git"
BRANCH="main"
DATE_TAG=$(date +%Y-%m-%d)

echo "[backup] Starting Hermes backup for $DATE_TAG..."

# Clean and recreate temp dir
rm -rf "$BACKUP_DIR"
mkdir -p "$BACKUP_DIR"

# Clone the repo (shallow, single branch)
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new"
git clone --depth 1 --branch "$BRANCH" "$REMOTE" "$BACKUP_DIR" 2>/dev/null || {
    echo "[backup] First run — initializing empty repo"
    git init -b "$BRANCH" "$BACKUP_DIR"
    git -C "$BACKUP_DIR" remote add origin "$REMOTE"
}

# Rsync relevant files from ~/.hermes/, excluding sensitive/large stuff
rsync -a --delete \
    --exclude=".env" \
    --exclude=".env.*" \
    --exclude="venv/" \
    --exclude="node_modules/" \
    --exclude="__pycache__/" \
    --exclude="*.pyc" \
    --exclude=".git/" \
    --exclude="hermes-agent/" \
    --exclude="image_cache/" \
    --exclude="audio_cache/" \
    --exclude="pastes/" \
    --exclude="logs/" \
    --exclude="state.db" \
    --exclude="state.db-wal" \
    --exclude="state.db-shm" \
    --exclude=".hermes_history" \
    "$REPO_DIR/" "$BACKUP_DIR/"

# Skip commit if nothing changed
cd "$BACKUP_DIR"
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "[backup] No changes — skipping commit"
    rm -rf "$BACKUP_DIR"
    exit 0
fi

git add -A
git commit -m "auto-backup $DATE_TAG"
export GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new"
git push origin "$BRANCH" 2>&1

echo "[backup] Backup complete for $DATE_TAG"

# Cleanup
rm -rf "$BACKUP_DIR"
