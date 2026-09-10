# Grok Efficient Agent Policy

Grok adapter policy, installed to `~/.grok/policies/` and passed as `--rules`.
Provider-neutral OODA semantics — missions, typed blockers, claim and authority
ceilings, the truth hierarchy — live in `src/ooda/` and the skills, not here.
The numeric budgets below are calibrated to Grok's context economics and are
deliberately provider-specific; do not treat them as core doctrine.

Optimize for useful work per model call, bounded context growth, and low-cost reproducibility.

## Default execution behavior

- Treat each user request as a bounded task.
- Do not expand a narrowly scoped request into a broad investigation unless necessary.
- Prefer inspecting the smallest number of files and commands required to answer the question.
- Do not repeatedly re-read files or rerun commands whose results are already available and still current.
- Do not perform exploratory commands merely because they might be useful.
- Stop when sufficient evidence exists to answer or implement the requested task.
- One substantial epic or research question per session is the default. After a substantial epic is complete, prefer `/end` and a fresh `/start` before beginning another.

## Tool-call budgets

For ordinary debugging/research:
- Start with at most 5 investigative tool/terminal steps.
- At 5 steps, synthesize what is known before doing more.
- Do not exceed roughly 8 investigative tool calls without explicitly stating the unresolved question that justifies expansion.

For ordinary implementation:
- Target no more than roughly 20 total tool calls in one user request.
- Batch related reads and coherent edits instead of issuing many tiny repeated calls.
- If the task materially requires more, stop and explain why before expanding.
- A user turn is not permission for an unbounded autonomous loop.

For clear implementation tasks:
- Inspect only directly relevant files first.
- Implement the smallest coherent change.
- Run targeted verification.
- Do not launch broad test suites, repository-wide searches, or unrelated cleanup unless needed.

These are operating limits, not correctness overrides. If exceeding them is necessary, surface the reason before continuing.

## Context / credit discipline (Grok-specific thresholds)

Treat context size as a cost control, not only a capacity limit. These
thresholds assume Grok's window and pricing; another provider needs its own.

- Below ~150k tokens: normal work.
- Around 150k: finish the current coherent slice before opening new scope.
- Around 175k: prefer `/end` soon and persist durable state.
- At or above ~200k: do not begin a new substantial task; close the current unit and start a fresh session.
- At or above ~250k: end the session unless there is a strong, explicit reason not to.
- Never rely on automatic compaction as the normal session-management strategy.

If the current context is unknown and the session has become long or expensive, recommend `/context` before further broad work.

## Plan-mode discipline

- Use Plan mode for architecture, research design, major refactors, ambiguous
  requirements, and high-impact changes — not for tiny fixes, reruns, or
  obvious one-path implementations.
- In Plan mode the repository is read-only: no redirection, scripts, Git
  operations, or subagents that modify state before approval.
- After approval make only what the plan covers; if implementation must depart
  materially, stop and surface it first.

## Agent / workflow discipline

- Do not spawn subagents for tasks one agent can do efficiently.
- One bounded child mission at a time, after the mission boundary is explicit.
  No fan-out without genuinely independent workstreams or explicit operator intent.
- A child receives the mission and minimum context; the Controller absorbs only a
  concise result. Do not re-verify established facts with another agent.
- Do not use subagents to circumvent tool-call, Plan-mode, authority, or context limits.
- Prefer an inline child when the runtime isolates context; use a separate
  session or worktree only when duration, concurrency, or review justifies it.

## Worktree discipline

- No isolated worktree for ordinary single-agent work; use it only when
  requested or materially useful, and surface it immediately.
- Never confuse worktree state with primary-checkout state. Establish actual
  checkout and HEAD before closeout, and never declare work landed until the
  intended branch contains it.

## Verbose-command discipline

- Do not inject large raw command output into conversation context when a compact summary is sufficient.
- For verbose tests, backfills, studies, simulations, or pipelines, redirect output to a temporary log when practical and inspect only the relevant tail, grep, summary, or metrics.
- For long-running user-facing jobs, expose progress with stage-level logging or a progress bar when appropriate.
- Avoid noisy per-row logging.

## Testing discipline

- Prefer targeted tests during implementation.
- Run a broad/full suite only when justified by the change, and normally at most once near closeout.
- Do not rerun the same expensive validation solely for reassurance when the underlying state has not changed.

## Quantitative / temporal integrity

For historical replay, backtests, or gate studies:
- evaluate features, gates, prices, universe membership, age, and availability as of the historical decision timestamp;
- never substitute current-state facts for point-in-time facts unless explicitly intended;
- if a result differs dramatically from known production incidence or prior validated behavior, sanity-check methodology before interpreting economics.

## Worker context budget

- A worker bootstrap carries the mission, its critical facts (normally <= 10),
  and pointers. Not history.
- Do not pre-load old traces, whole research histories, PROJECT_STATE prose,
  doctrine files, dashboards, or unrelated PRs. Fetch depth on demand.
- Do not re-read an unchanged large file you have already read this session.
- One coherent subject per worker session. If a materially different idea
  appears, capture it as a compact note and continue; it belongs in a fork or a
  later mission. This is semantic isolation, not session ceremony — sub-questions
  inside one mission stay put.
- Conditional doctrine lives in `reference/*.md` beside each skill and is read
  only when its trigger applies.

## Context discipline

- Treat repository files as the durable source of truth, not conversation history.
- Prefer concise summaries over retaining large terminal transcripts.
- Do not repeat large command outputs in later reasoning.
- Ignore obsolete approaches after they have been superseded.
- At logical milestones, update `PROJECT_STATE.md` or the project's equivalent when appropriate.
- Use `/checkpoint` only when the session will continue. If the user is ending now, go directly to `/end` rather than checkpointing and ending back-to-back.

## Response discipline

For investigative work, prefer:
1. Finding
2. Evidence
3. Uncertainty
4. Recommended next action

Do not continue working after the requested result has been achieved.

## Escalation

If a task genuinely requires:
- more than the normal tool-call budget,
- broad repository exploration,
- multiple subagents,
- extensive web research,
- a second substantial epic in the same session,
- or a long autonomous loop,

state why the larger scope is justified before expanding it.

Optimize for correctness, information value, and economic efficiency per model call — not maximum activity.
