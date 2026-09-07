#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${OODA_BIN_DIR:-$HOME/.local/bin}"
mkdir -p "$BIN_DIR"

install_link() {
  local name="$1"
  local src="$2"
  local dst="$BIN_DIR/$name"

  if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
    echo "Already installed $dst -> $src"
    return 0
  fi

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    echo "Refusing to replace existing $dst" >&2
    echo "Remove or move it deliberately, then rerun install." >&2
    return 2
  fi

  ln -s "$src" "$dst"
  echo "Installed $dst -> $src"
}

install_link ooda "$ROOT/scripts/ooda"
install_link grok-safe "$ROOT/scripts/grok-safe"
