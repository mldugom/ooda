# Provider Flavors

Status: **implemented provider boundary with Grok as the sole active reference flavor. DeepSeek/CodeWhale is parked and unqualified.**

OODA core remains provider-neutral. A provider flavor adapts terminal execution, model selection, child isolation, permissions, telemetry, and provider-native skills without redefining project truth or authority.

## Core stays provider-neutral

The following do not belong to any provider:

- `PROJECT_STATE.md`;
- `.ooda/project.json`;
- `.ooda/work-orders/`;
- `.ooda/traces/`;
- `.ooda/project-view.json`;
- project-local research/code/docs;
- Git / PR state;
- roles, profiles, lenses, claim levels, authority, and human gates.

Provider changes must not require a project migration or replay of chat history.

## Flavor abstraction

Keep two concepts separate:

1. **Runner / harness** — terminal UX, tool execution, child-agent mechanism, permissions, context isolation, hooks.
2. **Inference provider** — model endpoint, model choice, effort controls, context limits, pricing/quota/balance.

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

A flavor may define launch/setup, provider-native skills, bounded child isolation, role/profile/lens rendering, model/effort, tool permissions, telemetry, capability diagnostics, and concise result return.

A flavor may **not** redefine work-order meaning, TRACE semantics, claim levels, human integration authority, merge/model-promotion/capital gates, objective-ladder semantics, project truth sources, or completed/current/provisional meaning.

## Grok flavor — active reference

Current reference behavior:

```text
Grok Build TUI
  -> OODA Controller
  -> one bounded Grok Workflow child when warranted
  -> concise result / TRACE
```

`grok-safe` is the active launcher. The supported Grok command status line exposes current project orientation and writes provider telemetry when Grok supplies it.

## DeepSeek / CodeWhale — parked experiment

OODA 0.4 briefly implemented a direct DeepSeek path using CodeWhale as the runner and V4 Pro / V4 Flash as the intended Controller/worker split. Dogfooding exposed enough runner churn, UI mismatch, telemetry ambiguity, and maintenance surface that the experiment was parked before provider qualification completed.

The implementation remains in-tree as dormant experimental material; normal operator entrypoints fail closed while it is parked. It is **not** a supported or qualified flavor.

See [`DEEPSEEK.md`](DEEPSEEK.md) for the archived experiment summary and [`BACKLOG.md`](BACKLOG.md) for re-entry criteria.

## Provider telemetry contract

Provider adapters may write the optional derived file:

```text
.ooda/session-telemetry.json
```

using `ooda/session-telemetry/v1`. Useful fields include provider, model, effort, context used/limit/percentage, session tokens, session cost, account balance, telemetry source, and update time.

Rules:

- missing remains unknown, never zero;
- provider-metered cost and runner-estimated cost are labeled differently;
- account balance is distinct from session cost;
- credentials are not written into project telemetry;
- telemetry must never become project authority;
- a telemetry failure must not break the provider terminal.

Grok supplies provider/session telemetry through its supported status payload. Grok Build account-level Extra Usage balance is not exposed there, so OODA does not scrape it.

The parked DeepSeek experiment demonstrated that account-balance access and runner telemetry are separate concerns; if revisited, each field must retain explicit provenance rather than being presented as equivalent billing truth.

## Qualification principle

Do not qualify a flavor from public benchmarks alone. Re-run the same read-only OODA orientation tasks against frozen project state and compare the recovered control truth to established repository truth.

### Tenniskal acceptance

A fresh provider should recover:

- R6 exploratory research is complete;
- `ALPHA_HYPOTHESES_V1` is frozen;
- R7 compute has not started;
- the next scientific gate is an R7 preregistration;
- no outcome join, ROI search, or frozen-definition change is authorized.

### Crypto-Innout acceptance

A fresh provider should recover:

- the program revisited the PIT substrate gate;
- historically downloadable data is not automatically decision-time available;
- the panel should reuse valid A1.4/A1.5, crowd-PIT, `pit_universe`, presence, and feature-registry machinery;
- new collectors are not automatically warranted;
- wallet/cluster state must remain as-of-T or missing;
- live-writer containment is a separate operational gate.

A flavor is useful only if it preserves approximately the same control truth, boundaries, and next gate without importing old chat context.

## Security and privacy

At minimum:

- never persist `.env`, API keys, private keys, wallet secrets, credentials, or unrelated private data in OODA state;
- provider adapters must honor project-local exclusions and tool permissions;
- switching hosted inference providers is a conscious decision for private/proprietary repositories;
- Git authentication remains distinct from provider authentication;
- provider changes do not grant merge, live-runtime, model-promotion, or capital authority.

## Current decision

**Grok is the sole active reference flavor. DeepSeek/CodeWhale is parked in the backlog.**

Do not reopen a broad provider matrix until provider diversity is again the highest-value constraint and a second flavor can meet the backlog re-entry criteria without destabilizing the working Grok path.
