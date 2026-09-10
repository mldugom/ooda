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
OLD_DEEPSEEK_DST="$BIN_DIR/deepseek-safe"
OLD_DEEPSEEK_MARKER="# OODA deepseek-safe source: $ROOT"
OS_NAME="${OODA_OS_NAME:-$(uname -s)}"
LEGACY_GROK_SKILLS_SOURCE='source "$HOME/repos/grok-skills/shell/grok-safe.zsh"'
LEGACY_GROK_SKILLS_COMMENT='# Grok safe launcher (managed by ~/repos/grok-skills)'

mkdir -p "$BIN_DIR"

install_wrapper() {
  local dst="$1"
  local marker="$2"
  local module="$3"
  cat > "$dst" <<EOF
#!/usr/bin/env bash
$marker
set -euo pipefail
ROOT="$ROOT"
PYTHONPATH="\$ROOT/src\${PYTHONPATH:+:\$PYTHONPATH}" exec python3 -m $module "\$@"
EOF
  chmod +x "$dst"
}

if [ -f "$OODA_DST" ] && grep -Fqx "$OODA_MARKER" "$OODA_DST"; then
  echo "Already installed $OODA_DST"
elif [ -L "$OODA_DST" ] && [ "$(readlink "$OODA_DST")" = "$OODA_LEGACY_SRC" ]; then
  rm "$OODA_DST"
  install_wrapper "$OODA_DST" "$OODA_MARKER" ooda.compat_entrypoint
  echo "Upgraded legacy OODA $OODA_DST"
elif [ -e "$OODA_DST" ] || [ -L "$OODA_DST" ]; then
  echo "Refusing to replace existing $OODA_DST" >&2
  echo "Remove or move it deliberately, then rerun install." >&2
  exit 2
else
  install_wrapper "$OODA_DST" "$OODA_MARKER" ooda.compat_entrypoint
  echo "Installed $OODA_DST"
fi

if [ -f "$SAFE_DST" ] && grep -Fqx "$SAFE_MARKER" "$SAFE_DST"; then
  echo "Already installed $SAFE_DST"
elif [ -f "$SAFE_DST" ] && grep -Fqx "$LEGACY_SAFE_MARKER" "$SAFE_DST"; then
  rm "$SAFE_DST"
  install_wrapper "$SAFE_DST" "$SAFE_MARKER" ooda.compat_grok_safe
  echo "Upgraded legacy OODA $SAFE_DST"
elif [ -L "$SAFE_DST" ] && [ "$(readlink "$SAFE_DST")" = "$SAFE_LEGACY_SRC" ]; then
  rm "$SAFE_DST"
  install_wrapper "$SAFE_DST" "$SAFE_MARKER" ooda.compat_grok_safe
  echo "Upgraded legacy OODA $SAFE_DST"
elif [ -e "$SAFE_DST" ] || [ -L "$SAFE_DST" ]; then
  echo "Refusing to replace existing $SAFE_DST" >&2
  echo "Remove or move it deliberately, then rerun install." >&2
  exit 2
else
  install_wrapper "$SAFE_DST" "$SAFE_MARKER" ooda.compat_grok_safe
  echo "Installed $SAFE_DST"
fi

# DeepSeek/CodeWhale was an unqualified experiment. Remove only the wrapper this
# checkout itself installed; never touch an unrelated executable with the same name.
if [ -f "$OLD_DEEPSEEK_DST" ] && grep -Fqx "$OLD_DEEPSEEK_MARKER" "$OLD_DEEPSEEK_DST"; then
  rm "$OLD_DEEPSEEK_DST"
  echo "Removed obsolete OODA-managed $OLD_DEEPSEEK_DST"
fi

case ":${PATH:-}:" in
  *":$BIN_DIR:"*) ;;
  *)
    shell_name="$(basename "${SHELL:-sh}")"
    case "$shell_name" in
      zsh) rc_file="$HOME/.zshrc" ;;
      bash)
        if [ "$OS_NAME" = "Darwin" ]; then rc_file="$HOME/.bash_profile"; else rc_file="$HOME/.bashrc"; fi
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

# Remove only the exact legacy grok-skills hook known to shadow OODA's launcher.
shell_name="$(basename "${SHELL:-sh}")"
case "$shell_name" in
  zsh) rc_file="$HOME/.zshrc" ;;
  bash)
    if [ "$OS_NAME" = "Darwin" ]; then rc_file="$HOME/.bash_profile"; else rc_file="$HOME/.bashrc"; fi
    ;;
  *) rc_file="$HOME/.profile" ;;
esac
if [ -f "$rc_file" ] && grep -Fqx "$LEGACY_GROK_SKILLS_SOURCE" "$rc_file"; then
  tmp="$(mktemp)"
  grep -Fvx "$LEGACY_GROK_SKILLS_SOURCE" "$rc_file" | grep -Fvx "$LEGACY_GROK_SKILLS_COMMENT" > "$tmp" || true
  cp "$rc_file" "$rc_file.ooda-backup.$(date +%Y%m%d_%H%M%S)"
  mv "$tmp" "$rc_file"
  echo "Removed legacy grok-skills grok-safe shell hook from $rc_file"
  echo "Run: unset -f grok-safe 2>/dev/null || true"
fi
