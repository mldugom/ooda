# Provider Flavors

Status: **implemented provider boundary with one reference flavor (Grok) and one experimental/unqualified flavor (DeepSeek).**

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

## Grok flavor — reference

Current reference behavior:

```text
Grok Build TUI
  -> OODA Controller
  -> one bounded Grok Workflow child when warranted
  -> concise result / TRACE
```

`grok-safe` remains the reference launcher. The supported Grok command status line exposes current project orientation and writes provider telemetry when Grok supplies it.

## DeepSeek flavor — experimental / unqualified

OODA 0.4 adds a direct DeepSeek path with no Claude or other inference provider in the loop:

```text
DeepSeek-TUI
  -> DeepSeek V4 Pro Controller
  -> one DeepSeek V4 Flash bounded child
  -> concise result / TRACE
```

DeepSeek-TUI is a community-maintained terminal runner listed in DeepSeek's official `awesome-deepseek-agent` integration documentation. It is not the official DeepSeek Harness. OODA uses it here because the current runner exposes the skills, sandbox, subagent, model-selection, and turn-hook capabilities needed by the existing OODA contract. DeepSeek's official Harness remains developer preview and is not the 0.4 execution dependency.

Commands:

```bash
ooda setup deepseek
ooda doctor --provider deepseek
deepseek-safe
```

Controller default model: `deepseek-v4-pro`.
Bounded child default model: `deepseek-v4-flash`.

DeepSeek remains **UNQUALIFIED** until it passes the frozen Tenniskal and Crypto-Innout orientation cases plus one Pro -> Flash child delegation. Implementation alone is not qualification. See [`DEEPSEEK.md`](DEEPSEEK.md).

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

Grok supplies a provider-metered session cost through its supported status payload, but the Grok Build account-level Extra Usage balance is not exposed there; OODA does not scrape it.

DeepSeek-TUI can supply turn/session telemetry. When it supplies a session-cost value OODA labels it as an estimate. DeepSeek's documented `/user/balance` endpoint can supply actual account balance when `DEEPSEEK_API_KEY` is available to the OODA process; balance calls are cached.

## Model-tier routing

Model tier is execution economics, not doctrine.

Current DeepSeek default:

```text
V4 Pro
  -> Controller orientation
  -> consequential research design
  -> validation when needed

V4 Flash
  -> bounded implementation
  -> code archaeology
  -> tests
  -> documentation / mechanical work
```

A mission may deliberately choose Pro for a worker when the work requires it. The work-order contract, not model brand, determines scope and authority.

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

**Grok remains the qualified reference. DeepSeek is now implemented as the second experimental flavor and must earn qualification through repository-specific read-only tests.**

Do not build a broad provider matrix until dogfooding shows another provider is worth the additional adapter surface.
