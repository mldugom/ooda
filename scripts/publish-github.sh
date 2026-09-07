#!/usr/bin/env bash
set -euo pipefail
OWNER="${OODA_GITHUB_OWNER:-mldugom}"
NAME="${OODA_GITHUB_REPO:-ooda}"
VISIBILITY="${OODA_GITHUB_VISIBILITY:-private}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if git remote get-url origin >/dev/null 2>&1; then
  echo "origin already exists: $(git remote get-url origin)" >&2
  exit 2
fi

if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh repo create "$OWNER/$NAME" "--$VISIBILITY" --source=. --remote=origin --push
  echo "Published $OWNER/$NAME"
  exit 0
fi

echo "GitHub CLI is unavailable or not authenticated." >&2
echo "Create an empty $VISIBILITY repository named $OWNER/$NAME, then run:" >&2
echo "  git remote add origin git@github.com:$OWNER/$NAME.git" >&2
echo "  git push -u origin main" >&2
exit 3
