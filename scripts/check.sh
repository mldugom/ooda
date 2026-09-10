#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

test -s pyproject.toml
python3 -m compileall -q src
python3 -m unittest discover -s tests -v

for f in examples/work-order.json examples/work-order-specialist.json examples/trace.json examples/projects/*.json; do
  "$ROOT/scripts/ooda" doctor "$f" >/dev/null
done

# src/ooda/resources is the single source for skills and references. There is no
# second editable copy to drift, and tests/test_progressive_disclosure.py fails
# if one reappears or if any `reference/X.md` a skill names is not installed.
for f in \
  src/ooda/resources/EFFICIENT_AGENT.md \
  src/ooda/resources/grok/skills/ooda/SKILL.md \
  src/ooda/resources/grok/skills/ooda-controller/SKILL.md; do
  test -s "$f"
done

for f in src/ooda/resources/reference/*.md; do
  test -s "$f"
done

# Prove the installed layout resolves, exactly as an operator would get it.
INSTALL_CHECK="$(mktemp -d)"
trap 'rm -rf "$INSTALL_CHECK"' EXIT
GROK_HOME="$INSTALL_CHECK" bash "$ROOT/scripts/install-grok.sh" >/dev/null
test -s "$INSTALL_CHECK/skills/ooda/reference/predictive-science.md"
test -s "$INSTALL_CHECK/skills/ooda-controller/reference/blocker-semantics.md"

PYTHONPATH="$ROOT/src" python3 -m ooda.cli help >/dev/null
PYTHONPATH="$ROOT/src" python3 -c 'import ooda.grok_safe' >/dev/null

echo "OODA CHECK: PASS"
