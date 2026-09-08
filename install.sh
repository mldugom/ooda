#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$ROOT/scripts/install-cli.sh"
bash "$ROOT/scripts/install-grok.sh"

cat <<'EOF'

OODA installed.

Everyday commands:
  ooda help
  ooda init ...
  ooda doctor
  ooda mission ...
  ooda trace ...
  ooda dashboard

Grok:
  grok-safe
  /ooda-controller
  /ooda <mission-file>

DeepSeek (experimental / unqualified until project orientation checks pass):
  npm install -g --prefix "$HOME/.local" codewhale
  ooda setup deepseek
  ooda doctor --provider deepseek
  deepseek-safe

Pip users run `ooda setup` once to install the Grok skills/policy.
EOF
