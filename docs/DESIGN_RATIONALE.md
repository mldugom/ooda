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

This avoids multiplying agents for every domain while still supporting:
- statistics / data science / ML;
- software / SaaS / browser extensions;
- valuation / finance;
- portfolio / execution / risk;
- AI / agent engineering.

## Why claim rigor scales

The 2026 revised US model-risk guidance emphasizes validation rigor aligned to model approach, use, and materiality. OODA generalizes that principle without importing bank bureaucracy: a Discovery experiment should be cheap; a model used for consequential allocation or production should receive stronger validation and explicit limitations.

## Why substrate verification precedes sophistication

Google's Rules of Machine Learning explicitly recommends keeping the first model simple and testing the infrastructure independently from the learning algorithm. This matches the strongest lesson from LDPS: repeated later audits found material issues because earlier generations built sophistication before proving underlying data/transform/pricing truth.

## Lessons from the existing mldugom repositories

### Tenniskal
Keep:
- thin sequential research stages;
- point-in-time integrity;
- descriptive association != predictive alpha;
- pre-registration before outcome/P&L optimization;
- market economics as a later explicit gate.

### Crypto-Innout
Keep:
- research != production;
- runtime containment;
- protected artifacts;
- explicit human integration authority;
- no real-money execution by implication.

### LDPS
Keep:
- negative-result memory;
- walk-forward/sealed validation;
- placebo/selection accounting where material;
- deterministic artifacts;
- standing end-to-end verification.

Do not copy:
- giant catalogs as a default;
- documentation sprawl;
- factories before substrate truth;
- heavyweight validation for throwaway discovery.

### IOND
Keep:
- explicit assumptions;
- scenario/sensitivity reasoning;
- reverse valuation questions;
- honest separation of known cash flows from uncertain options;
- analytical product output.

This proves OODA must support fundamental analysis and product/software work, not only trading systems.

## Sources

- Air University material reproducing Boyd's OODA model and describing Orientation as the central synthesis/feedback function: https://www.airuniversity.af.edu/Portals/10/AUPress/Books/B_00165_GROTELUESCHEN_THE_HARMON_MEMORIAL_LECTURES_IN_MILITARY_HISTORY_1988_2017.pdf
- Lehman & Stanley, novelty search / deceptive objectives: https://pubmed.ncbi.nlm.nih.gov/20868264/
- Taleb on fragility/convex response: https://arxiv.org/abs/1808.00065
- Federal Reserve SR 26-2 revised model-risk guidance (2026): https://www.federalreserve.gov/supervisionreg/srletters/SR2602.htm
- Google Rules of Machine Learning: https://developers.google.com/machine-learning/guides/rules-of-ml/
