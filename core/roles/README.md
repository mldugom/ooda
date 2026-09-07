# Roles

A role answers: **who owns the next judgment or action?**

Roles encode accountability and authority. Expertise belongs in profiles; intellectual perspective belongs in lenses.

## Universal roles

| Role | Core question | Responsibility | Default authority |
|---|---|---|---|
| `controller` | What should happen next? | Establish state, route role/profile/lenses, bound scope/cost, decide stop/escalate | Dispatch only; no self-certification |
| `researcher` | What is true or potentially interesting? | Research, EDA, statistics, ML exploration, market/fundamental investigation | Discover; cannot promote claims |
| `product-strategist` | What problem is worth solving and for whom? | User problem, MVP boundary, value proposition, product experiments | Recommend scope; no release authority |
| `architect` | How should we test or build this? | Experiment design, systems design, interfaces, decomposition | Design; implementation requires Act authority |
| `engineer` | How do we implement this correctly? | Software, data, ML systems, apps, extensions, automation | Bounded implementation only |
| `validator` | How could this be wrong? | Independent challenge of research, models, code, security, controls, evidence | Recommend accept/reject; no self-merge |

## Finance roles

| Role | Core question | Responsibility | Default authority |
|---|---|---|---|
| `portfolio-manager` | Where should scarce risk capital go? | Allocation, correlation, concentration, opportunity cost, portfolio construction | Recommend within mandate; no live capital by default |
| `trader` | Can the modeled edge actually be captured? | Executable price, spread, liquidity, timing, slippage, adverse selection, CLV | Execution analysis; no strategy certification |
| `risk-manager` | What can hurt us badly? | Ruin, tails, exposure, leverage, model/operational failure, limits | Veto recommendation; live controls remain human/project authority |

## Anti-sprawl rule

Do not create `StatisticianBot`, `MLBot`, `BackendBot`, `ChromeBot`, or similar roles merely to encode expertise. Use a stable role plus a profile.

Examples:
- `researcher` + `quantitative-research`
- `researcher` + `fundamental-valuation`
- `engineer` + `browser-extension`
- `engineer` + `ml-engineering`
- `architect` + `agent-systems`
