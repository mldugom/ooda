#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

bash "$ROOT/scripts/install-cli.sh"
bash "$ROOT/scripts/install-grok.sh"

cat <<'EOF'

OODA installed.

Current commands:
  ooda help
  ooda init ...
  ooda doctor
  ooda mission ...
  ooda trace ...
  ooda dashboard

Grok Build — active reference provider:
  grok-safe
  /ooda-controller
  /ooda <mission-file>

Pip users run `ooda setup` once to install the Grok skills/policy.
EOF
