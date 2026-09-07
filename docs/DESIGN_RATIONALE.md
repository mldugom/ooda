# Design Rationale

## Why OODA is doctrine rather than branding

John Boyd's mature OODA representation treats orientation as central, with decisions as hypotheses, actions as tests, and feedback continuously reshaping observation/orientation. OODA therefore fits AI-assisted work better as a control grammar than as a linear checklist.

For OODA, the implication is: establish reality, synthesize through selected lenses, choose a bounded move, execute it, and learn from the result.

## Why bounded execution must preserve exploration

Kenneth Stanley and Joel Lehman's novelty-search work shows why optimization against an ambitious objective can be deceptive: apparent progress can lead to local dead ends, while novel stepping stones can reveal paths the objective gradient does not. OODA therefore allows a Stanley/Lehman lens in Orientation and a Discovery claim level where novelty can be explored cheaply without being mistaken for validated evidence.

## Why Taleb belongs in both research and engineering

Taleb's fragility/convexity framing emphasizes nonlinear response to variability and tail exposure. OODA applies that beyond portfolio management:

- bounded experiments preserve option value;
- irreversible architectural commitments deserve stronger scrutiny;
- real-money systems protect against ruin before optimizing expected return;
- via negativa asks what complexity/exposure should be removed instead of optimized.

## Why roles are not expertise bots

Stable roles represent accountability. Profiles represent expertise. Lenses represent intellectual perspective.

This avoids multiplying agents for every domain while still supporting statistics/data science/ML, software/products, valuation/finance, portfolio/execution/risk, and AI/agent engineering.

## Why claim rigor scales

Modern model-risk guidance emphasizes validation rigor aligned to model approach, use, and materiality. OODA generalizes that principle without importing institutional bureaucracy: a Discovery experiment should be cheap; a model used for consequential allocation or production should receive stronger validation and explicit limitations.

## Why substrate verification precedes sophistication

Google's Rules of Machine Learning recommends keeping early models simple and testing infrastructure independently from the learning algorithm. The broader engineering lesson is the same: sophisticated downstream analysis cannot rescue corrupted data, leaky transforms, broken pricing, stale state, or an unverified runtime substrate.

## General lessons encoded in OODA

### Sequential research

Keep:

- thin research stages;
- point-in-time integrity when temporal data matters;
- descriptive association != predictive utility;
- pre-registration/selection accounting when claims warrant it;
- economics/execution as explicit later gates when relevant.

### Runtime and production systems

Keep:

- research != production;
- runtime containment;
- protected artifacts;
- explicit human integration authority;
- no consequential production authority by implication.

### Validation-heavy research

Keep:

- negative-result memory;
- chronological/sealed validation when appropriate;
- placebo/selection accounting when material;
- deterministic artifacts;
- standing end-to-end verification.

Avoid:

- giant catalogs as a default;
- documentation sprawl;
- factories before substrate truth;
- heavyweight validation for throwaway discovery.

### Analytical products

Keep:

- explicit assumptions;
- scenario/sensitivity reasoning;
- reverse questions such as "what must be true for this result?";
- honest separation of known inputs from uncertain options;
- useful user-facing analytical output.

These lessons are intentionally cross-domain: OODA should support fundamental analysis, research, software/products, infrastructure, and trading systems without becoming specialized to any one of them.

## Sources

- Air University material reproducing Boyd's OODA model and describing Orientation as the central synthesis/feedback function: https://www.airuniversity.af.edu/Portals/10/AUPress/Books/B_00165_GROTELUESCHEN_THE_HARMON_MEMORIAL_LECTURES_IN_MILITARY_HISTORY_1988_2017.pdf
- Lehman & Stanley, novelty search / deceptive objectives: https://pubmed.ncbi.nlm.nih.gov/20868264/
- Taleb on fragility/convex response: https://arxiv.org/abs/1808.00065
- Federal Reserve model-risk guidance: https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm
- Google Rules of Machine Learning: https://developers.google.com/machine-learning/guides/rules-of-ml/
