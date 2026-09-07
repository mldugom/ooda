#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BIN_DIR="${OODA_BIN_DIR:-$HOME/.local/bin}"
OODA_DST="$BIN_DIR/ooda"
OODA_LEGACY_SRC="$ROOT/scripts/ooda"
OODA_MARKER="# OODA cli source: $ROOT"
SAFE_DST="$BIN_DIR/grok-safe"
SAFE_LEGACY_SRC="$ROOT/scripts/grok-safe"
SAFE_MARKER="# OODA grok-safe source: $ROOT"
LEGACY_SAFE_MARKER="# OODA source: $ROOT"
OS_NAME="${OODA_OS_NAME:-$(uname -s)}"

mkdir -p "$BIN_DIR"

install_ooda_wrapper() {
  cat > "$OODA_DST" <<EOF
#!/usr/bin/env bash
$OODA_MARKER
set -euo pipefail
ROOT="$ROOT"
PYTHONPATH="\$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}" exec python3 -m ooda.compat_entrypoint "\$@"
EOF
  chmod +x "$OODA_DST"
}

if [ -f "$OODA_DST" ] && grep -Fqx "$OODA_MARKER" "$OODA_DST"; then
  echo "Already installed $OODA_DST"
elif [ -L "$OODA_DST" ] && [ "$(readlink "$OODA_DST")" = "$OODA_LEGACY_SRC" ]; then
  rm "$OODA_DST"
  install_ooda_wrapper
  echo "Upgraded legacy OODA $OODA_DST"
elif [ -e "$OODA_DST" ] || [ -L "$OODA_DST" ]; then
  echo "Refusing to replace existing $OODA_DST" >&2
  echo "Remove or move it deliberately, then rerun install." >&2
  exit 2
else
  install_ooda_wrapper
  echo "Installed $OODA_DST"
fi

install_safe_wrapper() {
  cat > "$SAFE_DST" <<EOF
#!/usr/bin/env bash
$SAFE_MARKER
set -euo pipefail
ROOT="$ROOT"
PYTHONPATH="\$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}" exec python3 -m ooda.compat_grok_safe "\$@"
EOF
  chmod +x "$SAFE_DST"
}

if [ -f "$SAFE_DST" ] && grep -Fqx "$SAFE_MARKER" "$SAFE_DST"; then
  echo "Already installed $SAFE_DST"
elif [ -f "$SAFE_DST" ] && grep -Fqx "$LEGACY_SAFE_MARKER" "$SAFE_DST"; then
  rm "$SAFE_DST"
  install_safe_wrapper
  echo "Upgraded legacy OODA $SAFE_DST"
elif [ -L "$SAFE_DST" ] && [ "$(readlink "$SAFE_DST")" = "$SAFE_LEGACY_SRC" ]; then
  rm "$SAFE_DST"
  install_safe_wrapper
  echo "Upgraded legacy OODA $SAFE_DST"
elif [ -e "$SAFE_DST" ] || [ -L "$SAFE_DST" ]; then
  echo "Refusing to replace existing $SAFE_DST" >&2
  echo "Remove or move it deliberately, then rerun install." >&2
  exit 2
else
  install_safe_wrapper
  echo "Installed $SAFE_DST"
fi

case ":${PATH:-}:" in
  *":$BIN_DIR:"*)
    ;;
  *)
    shell_name="$(basename "${SHELL:-sh}")"
    case "$shell_name" in
      zsh) rc_file="$HOME/.zshrc" ;;
      bash)
        if [ "$OS_NAME" = "Darwin" ]; then
          rc_file="$HOME/.bash_profile"
        else
          rc_file="$HOME/.bashrc"
        fi
        ;;
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
