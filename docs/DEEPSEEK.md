# DeepSeek Flavor

Status: **experimental / unqualified** until it passes OODA's frozen Tenniskal and Crypto-Innout orientation cases plus one bounded child delegation.

OODA 0.4 adds a direct DeepSeek execution flavor without Claude or another inference provider in the loop.

```text
OODA core
   |
CodeWhale runner
   |
DeepSeek V4 Pro Controller
   |
DeepSeek V4 Flash bounded child
```

The community DeepSeek-TUI project was renamed to **CodeWhale** in 2026; the legacy `deepseek-tui` npm package is deprecated. CodeWhale remains a DeepSeek-capable terminal agent with skills, sandboxing, subagents, hooks, and direct DeepSeek provider support. OODA uses CodeWhale for this experimental terminal flavor. The official DeepSeek Harness remains a separate developer-preview option and is not the OODA 0.4 runner.

## Install

Install the current runner into the same user-local prefix OODA already uses:

```bash
npm install -g --prefix "$HOME/.local" codewhale
codewhale --version
```

OODA's launcher remains named `deepseek-safe` because the **provider flavor is DeepSeek** even though the terminal harness is CodeWhale.

Keep provider credentials local. OODA never asks you to commit a DeepSeek API key into a project file. If you want OODA to show the actual DeepSeek account balance, export the key in your shell so OODA can call DeepSeek's documented `/user/balance` endpoint:

```bash
export DEEPSEEK_API_KEY="..."
```

Then install the OODA flavor:

```bash
cd ~/repos/ooda
bash install.sh
ooda setup deepseek
ooda doctor --provider deepseek
```

Launch from an adopted project:

```bash
cd ~/repos/tenniskal
deepseek-safe
```

`ooda setup deepseek` writes current configuration and skills under `~/.codewhale/`. OODA also recognizes legacy `~/.deepseek/` skill/config state so an existing pre-rebrand install does not immediately break.

Inside CodeWhale, activate the `ooda-controller` skill. The Controller should remain on `deepseek-v4-pro`. For one bounded isolated worker, the Controller delegates to `deepseek-v4-flash` using CodeWhale's subagent mechanism and collects only the compact result needed to re-orient.

## Telemetry

`ooda setup deepseek` installs a non-fatal `turn_end` hook. The hook writes only derived provider/session telemetry to:

```text
.ooda/session-telemetry.json
```

The Control Room may show:

- provider and model;
- current conversation/context tokens against the model context;
- session tokens when the runner reports them;
- runner session-cost estimate when supplied;
- actual DeepSeek account balance when `DEEPSEEK_API_KEY` is available to OODA.

CodeWhale's session cost is labeled as an estimate (`~$`) because runner pricing metadata can lag provider billing. DeepSeek's `/user/balance` value is shown separately as account balance. Missing telemetry remains unknown; OODA does not turn missing values into zero.

The hook does not open a port. The only listener remains the optional local Control Room (`ooda dashboard`, default `127.0.0.1:8792`). Balance checks are outbound HTTPS requests and are cached for ten minutes.

If the user's CodeWhale config explicitly has `[hooks] enabled=false`, OODA installs its hook definition but does not silently enable all hooks. `ooda setup deepseek` warns instead.

## Qualification gate

Implementation is not qualification. Before DeepSeek is treated as a qualified OODA flavor, run these read-only checks from durable repository state.

### Tenniskal

The Controller must recover that:

- R6 exploratory work is complete;
- `ALPHA_HYPOTHESES_V1` is frozen;
- R7 compute has not started;
- the next scientific gate is an R7 preregistration;
- no outcome join, ROI search, or frozen-definition change is authorized.

### Crypto-Innout

The Controller must recover that:

- the program revisited the PIT substrate gate;
- historical availability is not decision-time availability;
- the PIT panel should reuse valid A1.4/A1.5, crowd-PIT, `pit_universe`, presence, and registry machinery;
- new collectors are not automatically warranted;
- wallet/cluster state must be as-of-T or remain missing;
- live-writer containment is a separate operational gate.

Then run one bounded Controller -> V4 Flash child delegation and confirm the child receives isolated task context and returns a concise result without changing authority.

Until those checks pass, the correct label is **DeepSeek: UNQUALIFIED**.
