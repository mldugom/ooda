#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

test -s pyproject.toml
python3 -m compileall -q src
python3 -m unittest discover -s tests -v

for f in examples/work-order.json examples/trace.json examples/projects/*.json; do
  "$ROOT/scripts/ooda" doctor "$f" >/dev/null
done

for f in \
  providers/grok/skills/ooda/SKILL.md \
  providers/grok/skills/ooda-controller/SKILL.md \
  src/ooda/resources/EFFICIENT_AGENT.md \
  src/ooda/resources/grok/skills/ooda/SKILL.md \
  src/ooda/resources/grok/skills/ooda-controller/SKILL.md; do
  test -s "$f"
done

PYTHONPATH="$ROOT/src" python3 -m ooda.cli help >/dev/null
PYTHONPATH="$ROOT/src" python3 -c 'import ooda.grok_safe' >/dev/null

echo "OODA CHECK: PASS"
