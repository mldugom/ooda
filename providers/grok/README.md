# Grok Provider Adapter

Grok is OODA V1's first execution provider, not OODA's identity.

## V1 behavior

Keep the existing Grok Build runtime and lifecycle unchanged.

A Grok session receives an `ooda/work-order/v1` contract and executes it under the selected role/profile/lenses while obeying the target project's local instructions.

The adapter must not duplicate project state or copy the full OODA repository into Grok's home directory.

## Optional `/ooda` skill

`providers/grok/skills/ooda/SKILL.md` is intentionally self-contained. It may be installed as one thin controller skill after shadow-mode usage begins.

The skill validates and interprets work orders; it does not replace `/start`, `/handoff`, or project-local rules.

## Provider-neutral boundary

Future providers must consume the same work-order semantics and emit the same trace semantics. Provider-specific session management stays here, not in `core/` or `contracts/`.
