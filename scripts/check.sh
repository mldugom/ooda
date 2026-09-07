#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
python3 -m unittest discover -s tests -v
for f in examples/work-order.json examples/trace.json examples/projects/*.json; do
  "$ROOT/scripts/ooda" validate "$f" >/dev/null
done
echo "OODA CHECK: PASS"
