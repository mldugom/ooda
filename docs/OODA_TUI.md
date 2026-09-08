# OODA Terminal Cockpit

OODA 0.4.1 adds an OODA-native terminal surface over the DeepSeek/CodeWhale runtime.

The operator-facing UI is OODA. CodeWhale is a hidden execution engine that supplies the DeepSeek model loop, local tools, sandboxing, sessions, compaction, and child-agent machinery.

```text
OODA TUI
   |
JSON-RPC over stdio
   |
codewhale app-server --stdio
   |
DeepSeek
```

No local listener port is required for the TUI. The browser Control Room remains a separate optional surface on its existing local HTTP port.

## Launch

From an OODA-adopted project:

```bash
cd ~/repos/tenniskal
ooda tui
```

The first interactive provider adapter is DeepSeek. The TUI starts a persistent `deepseek-v4-pro` thread through CodeWhale's documented `app-server --stdio` runtime API.

`deepseek-safe` remains available as the native CodeWhale TUI for debugging and provider-level inspection. Normal OODA operation should prefer `ooda tui` once the DeepSeek flavor is qualified.

## Screen

The terminal cockpit emphasizes current control state rather than reproducing the browser dashboard:

- project sidebar;
- current objective / current ladder rung;
- current human dependency or blocker;
- compact `OBSERVE -> ORIENT -> DECIDE -> ACT -> VERIFY` rail;
- objective ladder;
- latest material decision and immediate consequence;
- next provisional rung if the current gate passes;
- current worker/work-order state;
- provider/model/context/cost/balance footer when structured telemetry exists.

Context or session-cost values remain `n/a` when CodeWhale's stdio control transport does not expose authoritative usage. OODA does not invent token counts or infer cost from text length. DeepSeek account balance is read from the provider's balance endpoint when `DEEPSEEK_API_KEY` is exported.

## OODA slash commands

The OODA TUI implements OODA-owned slash commands directly:

```text
/ooda-controller <thought>
/ooda <mission or work-order path>
/refresh
/help
/quit
```

`/ooda-controller` and `/ooda` are not screen-scraped CodeWhale commands. OODA expands them into explicit runtime prompts that invoke the installed OODA Controller or worker skill in the same persistent DeepSeek thread.

Example:

```text
/ooda-controller where are we?
```

becomes an instruction to use the `ooda-controller` skill with `where are we?` as the operator input.

Provider-native CodeWhale slash menus such as `/plugin` are intentionally not forwarded through the app-server transport. Use `deepseek-safe` when native CodeWhale maintenance commands are needed.

## Authority

The TUI is an operator surface, not a new source of truth. Durable repository state, Git, work orders, traces, project-view state, tests, and explicit human gates remain authoritative.
