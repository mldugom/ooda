# Grok provider flavor

Grok is the current reference flavor for OODA.

## Where the skills live

The authoritative source for every provider skill and reference doc is:

```
src/ooda/resources/
├── EFFICIENT_AGENT.md              runner policy (Grok adapter)
├── reference/                      conditional doctrine, single source
└── grok/skills/{ooda,ooda-controller}/SKILL.md
```

There is deliberately **one** copy. An earlier layout kept an editable duplicate
under `providers/*/skills/`, which could drift from the packaged copy without CI
noticing. If you are looking for the skill text, edit it under
`src/ooda/resources/` — nowhere else.

## Install

```bash
bash scripts/install-grok.sh     # symlink/copy from a checkout
ooda setup                       # pip installs
```

Both install the two skills, the efficiency policy, and the `reference/` files
each skill can load on demand. `ooda doctor --install` verifies that every
reference a skill names actually resolves after installation.

## What is Grok-specific

Runner flags (`--rules`, `--max-turns`, `--no-subagents`), the `~/.grok/skills`
layout, child-agent dispatch, status line, and xAI cost telemetry. Core OODA
semantics — missions, typed blockers, claim/authority ceilings, traces, the truth
hierarchy — are provider-neutral and live in `src/ooda/`.
