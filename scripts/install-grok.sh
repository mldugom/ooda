#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RES="$ROOT/src/ooda/resources"
GROK_HOME_DIR="${GROK_HOME:-$HOME/.grok}"
mkdir -p "$GROK_HOME_DIR/skills"

# References each skill may load on demand. Keep in step with src/ooda/layout.py.
refs_for() {
  case "$1" in
    ooda-controller) echo "predictive-science.md blocker-semantics.md validation-routing.md visualization.md routing-vocabulary.md" ;;
    ooda)            echo "predictive-science.md visualization.md validation-routing.md documentation-impact.md runtime-reliability.md" ;;
  esac
}

is_legacy_ooda_skill_link() {
  local name="$1"
  local dst="$2"
  [ -L "$dst" ] || return 1
  local target
  target="$(readlink "$dst")"
  case "$target" in
    "$ROOT/providers/grok/skills/$name"|*/providers/grok/skills/"$name") return 0 ;;
    *) return 1 ;;
  esac
}

install_skill() {
  local name="$1"
  local src="$RES/grok/skills/$name/SKILL.md"
  local dst="$GROK_HOME_DIR/skills/$name"

  if [ ! -f "$src" ]; then
    echo "Missing OODA Grok skill: $src" >&2
    return 1
  fi

  # Pre-vnext installed the whole skill directory as a symlink into
  # providers/grok/skills/<name>. Those source directories were removed when
  # skills became packaged resources, leaving a dangling symlink that makes
  # mkdir fail. Migrate only that known OODA-owned shape; arbitrary symlinks are
  # never replaced.
  if [ -L "$dst" ]; then
    if is_legacy_ooda_skill_link "$name" "$dst"; then
      rm "$dst"
      echo "Migrated legacy OODA skill link: $dst"
    else
      echo "Refusing to replace unrelated skill symlink $dst -> $(readlink "$dst")" >&2
      return 2
    fi
  fi

  if [ -e "$dst/SKILL.md" ] && ! cmp -s "$src" "$dst/SKILL.md"; then
    echo "Refusing to replace differing $dst/SKILL.md" >&2
    echo "Remove it deliberately if you want to reinstall /$name." >&2
    return 2
  fi

  mkdir -p "$dst/reference"
  cp "$src" "$dst/SKILL.md"
  for ref in $(refs_for "$name"); do
    cp "$RES/reference/$ref" "$dst/reference/$ref"
  done
  echo "Installed /$name with $(refs_for "$name" | wc -w) on-demand references: $dst"
}

install_skill ooda
install_skill ooda-controller

mkdir -p "$GROK_HOME_DIR/policies"
cp "$RES/EFFICIENT_AGENT.md" "$GROK_HOME_DIR/policies/EFFICIENT_AGENT.md"
echo "Installed efficiency policy: $GROK_HOME_DIR/policies/EFFICIENT_AGENT.md"
echo "Existing Grok lifecycle skills are untouched."
