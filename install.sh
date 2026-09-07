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
  /ooda-controller
  /ooda <mission-file>
EOF
