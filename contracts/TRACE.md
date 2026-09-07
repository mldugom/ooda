# `ooda/trace/v1`

A trace records decision provenance without storing private chain-of-thought.

It is not a transcript.

It records:
- work-order ID;
- provider/model/agent when known;
- repository base/head and PR when relevant;
- concise Observe / Orient / Decide / Act summaries;
- result state;
- verification;
- costs/turns/tool calls when known;
- material findings, especially negative findings;
- human gate or next decision.

The trace is intended to become the provider-neutral input to Agent Ops Monitor after V1 shadow mode proves useful.
