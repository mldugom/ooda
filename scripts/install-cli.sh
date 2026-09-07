#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${OODA_BIN_DIR:-$HOME/.local/bin}"
mkdir -p "$BIN_DIR"
DST="$BIN_DIR/ooda"
if [ -e "$DST" ] || [ -L "$DST" ]; then echo "Refusing to replace existing $DST" >&2; exit 2; fi
ln -s "$ROOT/scripts/ooda" "$DST"
echo "Installed $DST -> $ROOT/scripts/ooda"
