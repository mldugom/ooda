# Claim Levels

Use the cheapest rigor that can honestly support the claim.

## DISCOVERY

Purpose: learn quickly and cheaply.

Allowed:
- exploratory analysis;
- rough models and correlations;
- visual investigation;
- small product prototypes;
- fast falsification;
- novelty search.

Requirements:
- obvious leakage and data errors still forbidden;
- result must be labeled discovery;
- cannot be promoted to a trusted model/strategy merely because it looks good;
- preserve a negative result when forgetting it would cause repeated waste.

## EVIDENCE

Purpose: determine whether a discovery survives meaningful scrutiny.

Typical requirements when relevant:
- point-in-time correctness;
- temporal/OOS validation;
- realistic economics;
- reproducibility;
- benchmark or simpler alternative;
- uncertainty/sensitivity analysis;
- enough sample to make the claim useful.

## QUALIFICATION

Purpose: determine whether the result is safe enough to rely upon for a consequential decision.

Typical requirements when relevant:
- frozen specification/data/artifact provenance;
- preregistration or explicit selection accounting;
- sealed or prospective evidence;
- independent validation;
- deterministic/reproducible artifacts;
- stress/robustness review;
- execution/portfolio/risk review for trading;
- security/reliability review for production software;
- explicit human promotion gate.

Qualification is not universal bureaucracy. Rigor scales with use, materiality, and downside.
