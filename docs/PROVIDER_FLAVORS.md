# Provider Flavors

Status: deferred design plan. Current OODA behavior remains Grok-first until a provider-port mission is explicitly commissioned.

## Why this exists

OODA is intended to be provider-neutral. The durable control system should survive a change in terminal agent, model vendor, or inference backend without forcing a project migration or replaying conversational history.

The core doctrine and project state must remain independent of any one provider:

- `PROJECT_STATE.md`
- `.ooda/project.json`
- `.ooda/work-orders/`
- `.ooda/traces/`
- `.ooda/project-view.json`
- project-local research/code/docs
- Git / PR state
- roles, profiles, lenses, claim levels, authority, and human gates

Provider-specific code should only adapt how an agent is launched, how bounded child context is created, how tools are exposed, and how results return to the same durable OODA artifacts.

## Current practical bridge

When one Grok Build quota is constrained, the lowest-risk short-term continuity path is to keep using the existing Grok flavor from another authorized Grok terminal/session, rather than changing the OODA execution model mid-research.

This bridge is operational, not architectural. OODA project state should not encode the identity of the human account used to invoke the provider. Git ownership/credentials, project authority, protected refs, and local secrets remain separate concerns and must be verified before writes.

No provider-port implementation is required merely to continue work through another authorized Grok terminal.

## Flavor abstraction

A future flavor should separate two concepts:

1. **Runner / harness** — terminal agent UX, tool execution, child/subagent mechanism, permissions, context isolation.
2. **Inference provider** — model endpoint, model choice, reasoning/effort controls, context limits, pricing/quota.

Conceptually:

```text
                     OODA CORE
                         |
      +------------------+------------------+
      |                  |                  |
 project state       work orders          traces
 project view        authority            gates
 ladder/timeline     roles/lenses         doctrine
      |                  |                  |
      +------------------+------------------+
                         |
                  PROVIDER FLAVOR
                         |
             runner + inference provider
```

The provider flavor must not redefine OODA semantics.

## Provider adapter responsibilities

A flavor may define:

- how to launch the terminal agent;
- where provider-native skill/agent files are installed;
- how one bounded child worker gets an isolated context;
- how role/profile/lenses/claim metadata are rendered into provider-native instructions;
- model and reasoning-effort selection;
- tool/permission restrictions;
- how work-order scope and stop conditions are supplied;
- how the child returns a concise result/TRACE-compatible handoff;
- provider capability checks such as child-agent availability or quota warnings.

A flavor may **not** redefine:

- work-order schema or meaning;
- TRACE semantics;
- claim levels;
- human integration authority;
- merge/model-promotion/capital gates;
- objective-ladder semantics;
- project truth sources;
- completed/current/provisional meaning;
- scientific or project-local invariants.

## Candidate UX

Exact CLI names are not frozen. A later design mission may evaluate a surface such as:

```bash
ooda setup grok
ooda setup <provider>
ooda run --flavor grok
ooda run --flavor <provider>
ooda doctor
```

or a persistent provider preference.

The front door should stay simple. Provider configuration must not turn OODA into a general-purpose model-router product.

## Candidate future flavors

These are possibilities, not selected dependencies or approved implementation work:

- Grok Build / xAI — current reference flavor.
- Google terminal-agent stack — possible hosted bridge when its quota/economics are useful.
- Local / Ollama-backed execution — possible low-cost/private worker path when model capability is sufficient.
- Other hosted inference providers — evaluate only when cost, capability, privacy, or availability creates a real reason.
- Pi — revisit when the intended Pi workflow is available and worth integrating.

No specific non-Grok provider is currently preferred or qualified by this document.

## Qualification principle

Do not qualify a flavor from public benchmarks alone. Re-run the same **read-only OODA orientation tasks** against frozen project state and compare the result to established truth.

Good acceptance cases include:

### Tenniskal

A fresh provider should recover from durable state that:

- R6 exploratory work is complete;
- `ALPHA_HYPOTHESES_V1` is frozen;
- R7 compute has not started;
- the next scientific gate is an R7 preregistration;
- no outcome join, ROI search, or frozen-definition change is authorized.

### Crypto-Innout

A fresh provider should recover that:

- the program revisited the PIT substrate gate;
- historical availability is not equivalent to decision-time availability;
- the panel should reuse existing A1.4/A1.5, crowd-PIT, `pit_universe`, presence, and registry machinery where valid;
- new collectors are not automatically warranted;
- wallet/cluster state must remain as-of-T or missing;
- live-writer containment is a separate operational gate.

A flavor is useful only if it preserves approximately the same control truth, boundaries, and next gate without importing old chat context.

## Model-tier routing

A future flavor may use different model tiers for different bounded roles, but OODA should treat this as execution economics rather than doctrine.

For example:

```text
strongest available model
  -> Controller orientation
  -> consequential research design
  -> independent validation

cheaper/local model when sufficient
  -> bounded implementation
  -> code archaeology
  -> tests
  -> documentation/mechanical work
```

The work-order contract, not the model brand, determines scope and authority.

## Security and privacy

Provider portability must make secret handling stricter, not looser.

At minimum:

- never send `.env`, API keys, private keys, wallet secrets, credentials, or unrelated private data to a provider;
- provider adapters should honor project-local exclusions and tool permissions;
- switching inference providers should be a conscious decision when private/proprietary repositories are involved;
- Git authentication must remain distinct from model-provider authentication;
- provider changes do not grant additional merge, live-runtime, or capital authority.

## Deferred implementation plan

When provider portability becomes the highest-value OODA product task, commission one bounded architecture/implementation slice:

1. inventory Grok-specific launcher/setup behavior;
2. extract the minimum provider-adapter interface while preserving Grok behavior exactly;
3. choose one second flavor based on the actual constraint at that time;
4. generate provider-native Controller/worker instructions from the same OODA semantics where practical;
5. add `ooda doctor` capability diagnostics;
6. validate the second flavor against frozen Tenniskal and Crypto-Innout orientation cases;
7. only then consider additional providers.

Avoid building a broad provider matrix before a second provider is actually needed.

## Current decision

**KEEP USING GROK FOR NOW.**

The provider-port project is intentionally parked. The immediate continuity strategy is to use an authorized Grok terminal with available quota and continue letting Git + OODA durable state carry project truth. Revisit provider flavors when the quota/provider constraint again becomes material or when Pi is ready.
