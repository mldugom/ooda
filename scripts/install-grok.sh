#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GROK_HOME_DIR="${GROK_HOME:-$HOME/.grok}"
mkdir -p "$GROK_HOME_DIR/skills"

install_skill() {
  local name="$1"
  local src="$ROOT/providers/grok/skills/$name"
  local dst="$GROK_HOME_DIR/skills/$name"

  if [ ! -f "$src/SKILL.md" ]; then
    echo "Missing OODA Grok skill: $src/SKILL.md" >&2
    return 1
  fi

  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    echo "Already installed /$name: $dst -> $src"
    return 0
  fi

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    echo "Refusing to replace existing $dst" >&2
    echo "Remove it deliberately if you want to reinstall /$name." >&2
    return 2
  fi

  ln -s "$src" "$dst"
  echo "Installed /$name as symlink: $dst -> $src"
}

install_skill ooda
install_skill ooda-controller

echo "Existing Grok lifecycle skills are untouched."
