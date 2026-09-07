#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROK_HOME_DIR="${GROK_HOME:-$HOME/.grok}"
SRC="$ROOT/providers/grok/skills/ooda"
DST="$GROK_HOME_DIR/skills/ooda"

if [ ! -f "$SRC/SKILL.md" ]; then
  echo "Missing OODA Grok adapter: $SRC/SKILL.md" >&2
  exit 1
fi

mkdir -p "$GROK_HOME_DIR/skills"

if [ -e "$DST" ] || [ -L "$DST" ]; then
  echo "Refusing to replace existing $DST" >&2
  echo "Remove it deliberately if you want to reinstall." >&2
  exit 2
fi

# One symlink only: OODA stays authoritative in this repository.
ln -s "$SRC" "$DST"
echo "Installed /ooda as symlink: $DST -> $SRC"
echo "Existing Grok lifecycle skills are untouched."
