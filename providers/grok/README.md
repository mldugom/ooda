# Grok Provider Adapter

Grok is OODA V1's first execution provider, not OODA's identity.

## Current Grok skills

OODA exposes two separate Grok surfaces:

| Skill | Job |
|---|---|
| `/ooda <work-order>` | Worker adapter. Executes one bounded mission inside a target project under its role/profile/lenses/claim/authority. |
| `/ooda-controller [thought or control question]` | Thin cross-project Controller. Handles Intake, work-order Proposal/Construction, and Control without absorbing deep worker context. |

The separation is intentional: the Controller chooses **what work should happen and how it should be bounded**; `/ooda` workers load the detailed project context required to actually do it.

## `/ooda` worker behavior

Keep the existing Grok Build runtime and lifecycle unchanged.

A Grok worker session receives an `ooda/work-order/v1` contract and executes it under the selected role/profile/lenses while obeying the target project's local instructions.

The worker adapter does not replace `/start`, `/handoff`, Git authority, or project-local rules.

The worker should explicitly cycle through current-state observation, orientation, bounded decision, action, and re-observation rather than treating a work order as a blind completion command.

Before handoff it also performs a documentation-impact check. Material changes to domain/architecture/process/interface/operator/research understanding should update the smallest durable documentation artifact inside scope; trivial conceptual-no-change work should simply report `documentation impact: none`.

## `/ooda-controller` behavior

The Controller normally reads only compact cross-project control state:

- project registry / `.ooda/project.json`;
- concise `PROJECT_STATE.md`-style summaries;
- active work orders;
- latest useful traces;
- human gates;
- relevant PR state;
- freshness/blockers;
- Lawrence/ChatGPT's current raw thought.

It has three modes:

1. **Intake** — discuss/triage a raw thought without automatically spending agent resources.
2. **Proposal / Work-order construction** — turn an earned idea into a bounded worker mission with role/profile/lenses/claim/scope/verification/budget/stops/authority and foreseeable documentation impact.
3. **Control** — summarize what needs attention across projects and surface the next gate.

If deeper code, web, data, research, implementation, or validation context is required, the Controller delegates to the appropriate worker instead of doing that work itself.

If a robust work order cannot be constructed from compact control state, the Controller should request a short orientation spike under an existing substantive role (`researcher`, `architect`, `validator`, `product-strategist`, or narrowly `engineer`) and then build the final contract from the returned evidence.

This is why OODA does not need a separate permanent work-order-builder bot.

See `docs/CONTROLLER.md`, `docs/CONTROLLER_QUICKSTART.md`, and `docs/DOCUMENTATION_STEWARDSHIP.md`.

## Installation

Run from the OODA repository:

```bash
./scripts/install-grok.sh
```

The installer symlinks both skills back to the authoritative OODA repo:

```text
~/.grok/skills/ooda            -> ~/repos/ooda/providers/grok/skills/ooda
~/.grok/skills/ooda-controller -> ~/repos/ooda/providers/grok/skills/ooda-controller
```

It is idempotent when the expected symlink already exists and does not replace unrelated/existing Grok lifecycle skills.

## Provider-neutral boundary

Future providers must consume the same work-order semantics and emit the same trace semantics. Controller behavior is also provider-neutral conceptually; provider-specific session management stays under `providers/`, not in `core/` or `contracts/`.
