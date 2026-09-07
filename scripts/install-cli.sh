#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${OODA_BIN_DIR:-$HOME/.local/bin}"
OODA_DST="$BIN_DIR/ooda"
OODA_SRC="$ROOT/scripts/ooda"
SAFE_DST="$BIN_DIR/grok-safe"
SAFE_MARKER="# OODA source: $ROOT"

mkdir -p "$BIN_DIR"

if [ -L "$OODA_DST" ] && [ "$(readlink "$OODA_DST")" = "$OODA_SRC" ]; then
  echo "Already installed $OODA_DST -> $OODA_SRC"
elif [ -e "$OODA_DST" ] || [ -L "$OODA_DST" ]; then
  echo "Refusing to replace existing $OODA_DST" >&2
  echo "Remove or move it deliberately, then rerun install." >&2
  exit 2
else
  ln -s "$OODA_SRC" "$OODA_DST"
  echo "Installed $OODA_DST -> $OODA_SRC"
fi

if [ -f "$SAFE_DST" ] && grep -Fqx "$SAFE_MARKER" "$SAFE_DST"; then
  echo "Already installed $SAFE_DST"
elif [ -e "$SAFE_DST" ] || [ -L "$SAFE_DST" ]; then
  echo "Refusing to replace existing $SAFE_DST" >&2
  echo "Remove or move it deliberately, then rerun install." >&2
  exit 2
else
  cat > "$SAFE_DST" <<EOF
#!/usr/bin/env bash
$SAFE_MARKER
set -euo pipefail
ROOT="$ROOT"
PYTHONPATH="\$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}" exec python3 -m ooda.grok_safe "\$@"
EOF
  chmod +x "$SAFE_DST"
  echo "Installed $SAFE_DST"
fi

case ":${PATH:-}:" in
  *":$BIN_DIR:"*)
    ;;
  *)
    shell_name="$(basename "${SHELL:-sh}")"
    case "$shell_name" in
      zsh) rc_file="$HOME/.zshrc" ;;
      bash) rc_file="$HOME/.bashrc" ;;
      *) rc_file="$HOME/.profile" ;;
    esac
    path_line="export PATH=\"$BIN_DIR:\$PATH\""
    touch "$rc_file"
    if ! grep -Fqx "$path_line" "$rc_file"; then
      {
        printf '\n# OODA CLI\n'
        printf '%s\n' "$path_line"
      } >> "$rc_file"
      echo "Added $BIN_DIR to PATH in $rc_file"
    fi
    echo "Activate OODA in this shell now with:"
    echo "  export PATH=\"$BIN_DIR:\$PATH\""
    ;;
esac
