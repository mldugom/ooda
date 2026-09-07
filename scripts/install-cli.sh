#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${OODA_BIN_DIR:-$HOME/.local/bin}"
DST="$BIN_DIR/ooda"
SRC="$ROOT/scripts/ooda"

mkdir -p "$BIN_DIR"

if [ -L "$DST" ] && [ "$(readlink "$DST")" = "$SRC" ]; then
  echo "Already installed $DST -> $SRC"
  exit 0
fi

if [ -e "$DST" ] || [ -L "$DST" ]; then
  echo "Refusing to replace existing $DST" >&2
  echo "Remove or move it deliberately, then rerun install." >&2
  exit 2
fi

ln -s "$SRC" "$DST"
echo "Installed $DST -> $SRC"
