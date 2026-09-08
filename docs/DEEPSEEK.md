# DeepSeek Flavor — Parked Experiment

Status: **parked / unqualified**.

The September 2026 DeepSeek/CodeWhale experiment is not an active OODA provider path. Grok via `grok-safe` is the sole active reference flavor for now.

The experiment established that OODA can keep its project truth, work orders, traces, objective ladder, and authority semantics provider-neutral while adapting another terminal runtime. It also exposed enough integration friction that continuing the lane is not currently worth the operating cost.

Observed friction included:

- the `deepseek-tui` package being deprecated/renamed to CodeWhale during setup;
- mismatch between the provider runtime's native UI and the desired OODA operator cockpit;
- incomplete authoritative context/session-cost telemetry through the stdio integration path;
- additional maintenance surface for skills, hooks, runner compatibility, and provider-specific terminal behavior;
- the planned Tenniskal, Crypto-Innout, and bounded child-delegation qualification sequence remaining incomplete.

Current operating decision:

```text
OODA core
   |
Grok Build TUI
   |
grok-safe
   |
OODA Controller -> bounded Grok Workflow child
```

The DeepSeek implementation modules remain in-tree as dormant experimental material so the work is not lost. Public operator paths fail closed while the experiment is parked: `deepseek-safe`, `ooda setup deepseek`, `ooda doctor --provider deepseek`, and the CodeWhale-backed `ooda tui` path are not active workflows.

Do not treat prior implementation as qualification. If this provider lane is revisited, start from the re-entry criteria in [`BACKLOG.md`](BACKLOG.md) and re-run frozen read-only Tenniskal and Crypto-Innout orientation cases before any consequential use.

No DeepSeek credential belongs in repository state. Existing local CodeWhale/DeepSeek configuration may be removed by the operator independently; OODA does not delete user configuration automatically.
