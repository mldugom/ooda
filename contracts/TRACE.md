# `ooda/trace/v1`

A trace records decision provenance. It is not a transcript, and it is not a
place to restate the work order.

Its only job is to let a fresh session re-orient cheaply. Anything that does not
serve that job is weight.

## The compact durable record

```text
RESULT        completed | negative_finding | blocked | budget_exhausted | needs_human_gate
EVIDENCE      the finding, with sample/metric/uncertainty where empirical
ARTIFACTS     pointers, not contents
NON-CLAIMS    what this does NOT establish, and the claim ceiling reached
BLOCKER       typed, when blocked (below)
NEXT UNKNOWN  the highest-value uncertainty this exposed
HUMAN GATE    the decision needed, or none
STATE         branch / commit / PR pointer
```

**Do not duplicate mutable facts.** Branch, writer status, data clocks, PR state,
and evidence counts belong to the authoritative surface that owns them; a trace
that copies them is stale the moment it is written. Point instead.

`NON-CLAIMS` is not optional politeness. It is the field that stops a discovery
being read later as evidence.

## Typed blockers

A bare `blocked` is not a valid result. It loses the information that decides
what may still happen, and a controller that prioritises blocked missions will
then keep re-surfacing a stall that was never real.

```text
blocker_type        scientific | data | environment | authority | promotion | sequencing
blocked_for         exploration | evidence | qualification | production | capital
claim_ceiling       discovery | evidence | qualification | n-a
exploration_allowed yes | no
target              scientific/data blockers: the exact quantity or comparison affected
```

Two rules the system enforces in code (`ooda.policy`):

- **Stages describe evidence, not permission.** `sequencing` never bars work.
- **A claim ceiling is not a work ceiling.** Exploration survives every blocker
  except a scientific one covering exploration, and that binds only its target.

Before recording `blocked`, answer in writing: *is there a cheap, scientifically
honest experiment available now that does not violate the claim ceiling?*

See `reference/blocker-semantics.md` for worked cases.

## Result states

- `completed` — objective met with stated verification
- `negative_finding` — **a success.** No signal, insufficient sample, weak
  features, poorly conditioned target, not identifiable. Preserve it; it is what
  stops the next session repeating the work. Do not respond by adding features,
  trying more models, or moving the target.
- `blocked` — a typed, concrete dependency
- `budget_exhausted` — continuing needs a new resource decision
- `needs_human_gate` — an authority boundary was reached

## Quantitative evidence

For material quantitative work, preserve the smallest useful packet — question,
data and PIT semantics, analysis, key evidence table, interpretation, artifacts,
next unknown. It may live in the trace or in an authoritative research artifact
the trace points at. Do not write it twice.

## Backward compatibility

Traces written before vnext carry `result.state == "blocked"` with no blocker
object. They still load: `ooda.policy.parse_blocker` reads them as
`blocker_type: legacy`, which does not bar exploration but must be re-typed
before it can support a claim or a promotion.

## Control Room

The trace is an input to the Control Room, which remains a derived view. A
blocker that still permits exploration renders as such, so a project that can
keep moving is never displayed as one that cannot.

## Design principle

> The action is not operationally complete until its useful feedback can enter
> the next OODA loop — and no earlier than that.
