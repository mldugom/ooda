"""Deterministic OODA policy.

Agents reason and propose; this module decides. Everything here is a pure
function over plain data so CI can assert on it, because the failure this
module exists to prevent -- a bare ``blocked`` token stopping useful work --
came from semantics that lived only in prose.

Three policies live here:

* blocker semantics (typed, scoped)
* truth freshness/authority hierarchy
* validation routing by consequence
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# --------------------------------------------------------------------------
# Blocker semantics
# --------------------------------------------------------------------------

BLOCKER_TYPES = (
    "scientific",    # the data cannot identify the thing; no method fixes it
    "data",          # the data is absent or not yet joined
    "environment",   # this execution environment lacks host/files/credentials
    "authority",     # a human authority boundary
    "promotion",     # a claim/stage gate not yet met
    "sequencing",    # a historical stage label only -- never a real dependency
    "legacy",        # an untyped pre-vnext `blocked`; must be re-typed
)

BLOCKED_FOR = ("exploration", "evidence", "qualification", "production", "capital")

CLAIM_CEILINGS = ("discovery", "evidence", "qualification", "n-a")

# Ordered weakest -> strongest. "n-a" means no empirical claim is in play.
_CLAIM_ORDER = {"n-a": 0, "discovery": 1, "evidence": 2, "qualification": 3}

# What a mission intends to do, weakest -> strongest.
INTENTS = ("explore", "claim_evidence", "claim_qualification", "promote_production", "deploy_capital")

_INTENT_SCOPE = {
    "explore": "exploration",
    "claim_evidence": "evidence",
    "claim_qualification": "qualification",
    "promote_production": "production",
    "deploy_capital": "capital",
}

_INTENT_CLAIM = {
    "explore": "discovery",
    "claim_evidence": "evidence",
    "claim_qualification": "qualification",
    "promote_production": "qualification",
    "deploy_capital": "qualification",
}


class BlockerError(ValueError):
    """Raised when a blocker cannot be represented honestly."""


@dataclass(frozen=True)
class Blocker:
    """A typed, scoped blocker.

    ``scope`` is what the blocker actually prevents. ``target`` narrows a
    scientific blocker to the specific unidentifiable quantity, so refusing
    one target never silently refuses the whole research programme.
    """

    blocker_type: str
    blocked_for: Tuple[str, ...] = ()
    claim_ceiling: str = "n-a"
    target: Optional[str] = None
    note: str = ""

    def __post_init__(self) -> None:
        if self.blocker_type not in BLOCKER_TYPES:
            raise BlockerError(f"unknown blocker_type: {self.blocker_type!r}")
        bad = [s for s in self.blocked_for if s not in BLOCKED_FOR]
        if bad:
            raise BlockerError("unknown blocked_for: " + ", ".join(bad))
        if self.claim_ceiling not in CLAIM_CEILINGS:
            raise BlockerError(f"unknown claim_ceiling: {self.claim_ceiling!r}")

    # -- the two rules the audit says must never be re-litigated -------------

    @property
    def exploration_allowed(self) -> bool:
        """Whether exploration of this blocker's own subject may proceed.

        Derived from :func:`work_permitted` rather than re-deriving the rule, so
        a serialized blocker can never contradict the permission the system
        actually enforces. An earlier version answered this independently and
        reported ``True`` for a data/environment/authority/promotion blocker whose
        ``blocked_for`` included exploration, while ``work_permitted`` correctly
        refused -- a serialized field disagreeing with enforcement is exactly the
        class of defect typed blockers exist to remove.

        Evaluated on the blocker's own terms: a blocker naming a target speaks
        only about that target, which callers express by passing ``target`` to
        ``work_permitted`` directly.
        """
        return work_permitted(self, "explore").allowed

    @property
    def is_real_dependency(self) -> bool:
        """Sequencing is a label, not a dependency."""
        return self.blocker_type != "sequencing"

    @property
    def needs_retyping(self) -> bool:
        return self.blocker_type == "legacy"

    def to_dict(self) -> Dict[str, Any]:
        out: Dict[str, Any] = {
            "blocker_type": self.blocker_type,
            "blocked_for": list(self.blocked_for),
            "claim_ceiling": self.claim_ceiling,
            "exploration_allowed": self.exploration_allowed,
        }
        if self.target:
            out["target"] = self.target
        if self.note:
            out["note"] = self.note
        return out


def parse_blocker(value: Any) -> Optional[Blocker]:
    """Read a blocker from new typed form or a legacy bare token.

    Old traces carrying ``result.state == "blocked"`` and nothing else parse as
    ``legacy``: readable, flagged for re-typing, and -- deliberately -- not
    treated as a bar on exploration, since over-blocking is the documented
    failure mode.
    """
    if value in (None, "", {}):
        return None
    if isinstance(value, str):
        if value == "blocked":
            return Blocker(blocker_type="legacy", note="untyped pre-vnext blocker; re-type before relying on it")
        if value in BLOCKER_TYPES:
            return Blocker(blocker_type=value)
        raise BlockerError(f"cannot parse blocker from {value!r}")
    if isinstance(value, dict):
        raw_for = value.get("blocked_for") or ()
        if isinstance(raw_for, str):
            raw_for = (raw_for,)
        return Blocker(
            blocker_type=value.get("blocker_type") or "legacy",
            blocked_for=tuple(raw_for),
            claim_ceiling=value.get("claim_ceiling") or "n-a",
            target=value.get("target"),
            note=value.get("note") or "",
        )
    raise BlockerError(f"cannot parse blocker from {type(value).__name__}")


@dataclass(frozen=True)
class Permission:
    allowed: bool
    reason: str

    def __bool__(self) -> bool:  # convenience in asserts and `if`
        return self.allowed


def work_permitted(blocker: Optional[Blocker], intent: str, *, target: Optional[str] = None) -> Permission:
    """Decide whether `intent` may proceed under `blocker`.

    ``target`` is the quantity the mission is about; a scientific blocker only
    bites when the mission targets the same unidentifiable quantity.
    """
    if intent not in INTENTS:
        raise BlockerError(f"unknown intent: {intent!r}")
    if blocker is None:
        return Permission(True, "no blocker recorded")

    scope = _INTENT_SCOPE[intent]

    if blocker.blocker_type == "sequencing":
        return Permission(
            True,
            "sequencing is a historical stage label, not a dependency; it never bars work",
        )

    # A blocker that names a target bites only that target. This is what keeps a
    # missing sportsbook baseline from reading as "all research is blocked", and
    # an unidentifiable MFE from closing every other endpoint.
    if blocker.target is not None and target is not None and blocker.target != target:
        return Permission(
            True,
            f"{blocker.blocker_type} blocker applies to {blocker.target!r}, not {target!r}",
        )

    if blocker.blocker_type == "scientific":
        if scope in blocker.blocked_for:
            return Permission(False, f"scientifically blocked for {scope}: {blocker.note or blocker.target or 'not identifiable'}")
        return Permission(True, f"scientific blocker does not cover {scope}")

    if blocker.blocker_type == "legacy":
        if intent == "explore":
            return Permission(True, "legacy untyped blocker does not bar exploration; re-type it")
        return Permission(False, "legacy untyped blocker must be re-typed before a claim or promotion")

    # data / environment / authority / promotion
    if scope in blocker.blocked_for:
        return Permission(False, f"{blocker.blocker_type} blocker covers {scope}: {blocker.note}".rstrip(": "))
    return Permission(True, f"{blocker.blocker_type} blocker does not cover {scope}")


def claim_permitted(claim_ceiling: str, intent: str) -> Permission:
    """A claim ceiling caps claims; it never caps work."""
    if claim_ceiling not in CLAIM_CEILINGS:
        raise BlockerError(f"unknown claim_ceiling: {claim_ceiling!r}")
    if intent not in INTENTS:
        raise BlockerError(f"unknown intent: {intent!r}")
    if intent == "explore":
        return Permission(True, "exploration makes no claim, so no ceiling applies")
    wanted = _CLAIM_ORDER[_INTENT_CLAIM[intent]]
    if wanted > _CLAIM_ORDER[claim_ceiling]:
        return Permission(False, f"intent {intent} needs a claim above the {claim_ceiling} ceiling")
    return Permission(True, f"{intent} is within the {claim_ceiling} ceiling")


BLOCKER_CHALLENGE = (
    "Is there a cheap, scientifically honest experiment available now that does not "
    "violate the current claim or authority ceiling?"
)

# Compact form for output. The question is a control invariant, not a thing to
# reproduce in every answer -- restating it costs tokens on every blocked path
# and adds nothing a reader did not already know.
CHALLENGE_TAG = "Cheap honest experiment available?"


def blocker_challenge_required(blocker: Optional[Blocker]) -> bool:
    """Whether the controller must answer the challenge before declining to work.

    ``None`` returns True deliberately. The invariant guards a false negative --
    not working when useful work exists -- and that risk is present in both
    idle-on-block paths: returning BLOCK under a blocker that still permits
    exploration, and returning NO ACTION with no blocker at all. The second is
    the easier one to get wrong, so it is not exempt.

    This governs the *decision*, not the prose. Callers should render the answer
    with ``challenge_line``; the question itself does not need reproducing.
    """
    if blocker is None:
        return True
    return blocker.exploration_allowed


def challenge_line(answer_yes: bool, detail: str = "") -> str:
    """One-line rendering of the challenge answer.

    A `yes` names the experiment; a `no` must justify itself, because declining
    available work is the failure this whole mechanism exists to catch.
    """
    verdict = "yes" if answer_yes else "no"
    detail = detail.strip()
    if not detail:
        return f"{CHALLENGE_TAG} {verdict}"
    return f"{CHALLENGE_TAG} {verdict} — {detail}"


# --------------------------------------------------------------------------
# Truth freshness / authority hierarchy
# --------------------------------------------------------------------------

# Authority is a property of the QUESTION, not a global ranking. A single global
# order gets live operational facts right and scientific contracts wrong: the
# runtime does not know what target was frozen, and a frozen prereg does not know
# whether the collector is running now.
#
# Four domains is the whole ontology. Each tuple is weakest -> strongest, and
# derived surfaces stay lowest everywhere.
TRUTH_SOURCES = (
    "dashboard",       # derived convenience only
    "project_view",    # derived human orientation
    "project_state",   # compact durable orientation prose
    "trace",           # latest verified mission outcome
    "frozen_artifact", # prereg / frozen scientific contract
    "git",             # repository truth
    "runtime",         # live operational fact
)

_DERIVED_TAIL = ("dashboard", "project_view", "project_state")

FACT_DOMAINS = {
    # "is the collector running?" -- only the runtime knows.
    "operational": _DERIVED_TAIL + ("frozen_artifact", "trace", "git", "runtime"),
    # "what branch/HEAD exists?" -- Git owns repository truth.
    "repository": _DERIVED_TAIL + ("frozen_artifact", "trace", "runtime", "git"),
    # "what target/prereg was frozen?" -- the frozen artifact is the contract;
    # a later runtime or trace cannot retroactively change what was preregistered.
    "scientific_contract": _DERIVED_TAIL + ("runtime", "git", "trace", "frozen_artifact"),
    # "what did the last validated mission conclude?" -- the verified trace.
    "mission_outcome": _DERIVED_TAIL + ("runtime", "git", "frozen_artifact", "trace"),
}

DEFAULT_FACT_DOMAIN = "operational"

# Kept for callers that want the plain default ordering.
TRUTH_RANK = {name: i for i, name in enumerate(FACT_DOMAINS[DEFAULT_FACT_DOMAIN])}


def truth_rank(source: str, domain: str = DEFAULT_FACT_DOMAIN) -> int:
    """Authority of `source` for a question in `domain`. Higher wins."""
    if domain not in FACT_DOMAINS:
        raise ValueError(f"unknown fact domain: {domain!r}")
    order = FACT_DOMAINS[domain]
    if source not in order:
        raise ValueError(f"unknown truth source: {source!r}")
    return order.index(source)

DERIVED_SOURCES = frozenset({"dashboard", "project_view"})
PROSE_SOURCES = frozenset({"project_state", "project_view", "dashboard"})


@dataclass(frozen=True)
class TruthClaim:
    source: str
    value: Any
    note: str = ""

    def __post_init__(self) -> None:
        if self.source not in TRUTH_SOURCES:
            raise ValueError(f"unknown truth source: {self.source!r}")


@dataclass(frozen=True)
class TruthResolution:
    winner: TruthClaim
    stale: Tuple[TruthClaim, ...] = ()
    conflict: bool = False
    domain: str = DEFAULT_FACT_DOMAIN

    @property
    def stale_sources(self) -> Tuple[str, ...]:
        return tuple(c.source for c in self.stale)


def resolve_truth(
    claims: Sequence[TruthClaim], domain: str = DEFAULT_FACT_DOMAIN
) -> TruthResolution:
    """Highest-authority claim for this kind of question wins.

    Disagreeing lower-authority sources are flagged stale rather than silently
    dropped. `domain` scopes the ranking so no single source type outranks every
    other globally -- the runtime wins "is the collector running?", Git wins
    "what branch exists?", the frozen artifact wins "what was preregistered?",
    and the verified trace wins "what did the last mission conclude?".
    """
    if not claims:
        raise ValueError("resolve_truth requires at least one claim")
    ordered = sorted(claims, key=lambda c: truth_rank(c.source, domain), reverse=True)
    winner = ordered[0]
    stale = tuple(c for c in ordered[1:] if c.value != winner.value)
    return TruthResolution(winner=winner, stale=stale, conflict=bool(stale), domain=domain)


def is_derived(source: str) -> bool:
    """Derived surfaces never win a conflict."""
    return source in DERIVED_SOURCES


# --------------------------------------------------------------------------
# Validation routing by consequence
# --------------------------------------------------------------------------

CONSEQUENCE_CLASSES = ("low", "medium", "high")

# Any one of these makes work high-consequence.
HIGH_CONSEQUENCE_SIGNALS = frozenset({
    "qualification_claim",
    "production_promotion",
    "capital",
    "security_boundary",
    "live_data_mutation",
    "runtime_safety",
    "sealed_evidence_interpretation",
})

MEDIUM_CONSEQUENCE_SIGNALS = frozenset({
    "exploratory_research",
    "architecture_change",
    "data_transformation",
})


def consequence_class(signals: Iterable[str]) -> str:
    present = set(signals or ())
    if present & HIGH_CONSEQUENCE_SIGNALS:
        return "high"
    if present & MEDIUM_CONSEQUENCE_SIGNALS:
        return "medium"
    return "low"


@dataclass(frozen=True)
class ValidationRoute:
    consequence: str
    independent_validator: str  # "required" | "discretionary" | "not_required"
    deterministic_checks: bool
    reason: str


def validation_route(signals: Iterable[str], *, elevated_uncertainty: bool = False) -> ValidationRoute:
    """Route validation by consequence, not by habit.

    The point is independent error detection where an error would be expensive,
    not ceremony on every task.
    """
    cls = consequence_class(signals)
    if cls == "high":
        return ValidationRoute(cls, "required", True,
                               "consequential claim, promotion, capital, or runtime safety")
    if cls == "medium":
        return ValidationRoute(
            cls,
            "discretionary" if not elevated_uncertainty else "required",
            True,
            "deterministic checks always; independent validator when uncertainty or risk warrants",
        )
    return ValidationRoute(cls, "not_required", True,
                           "self-check and tests are sufficient for reversible local work")


# --------------------------------------------------------------------------
# Routing descriptors (role / profile / lens) -- optional by policy
# --------------------------------------------------------------------------

def descriptor_warranted(descriptor: Optional[str], *, changes_behavior: bool) -> bool:
    """A descriptor earns its tokens only when it changes worker behavior.

    The ablation found no measurable gain from role/profile/lens on ordinary
    data-science work, so they are optional aids, never mandatory ceremony.
    """
    return bool(descriptor) and changes_behavior


def lens_budget_ok(lenses: Sequence[str], *, justification: str = "") -> Tuple[bool, str]:
    """Default 0-1 lenses; 2+ needs a concrete stated reason; 3 is the hard cap."""
    n = len(lenses or ())
    if n <= 1:
        return True, "within default lens budget"
    if n > 3:
        return False, "more than three lenses is never warranted for one bounded action"
    if not justification.strip():
        return False, f"{n} lenses require a concrete justification"
    return True, f"{n} lenses justified: {justification.strip()}"


# --------------------------------------------------------------------------
# PROJECT_STATE hygiene
# --------------------------------------------------------------------------

# Facts that belong to an authoritative surface, not to durable prose. A summary
# that restates them is stale the moment it is written -- this is the shape of
# the "collection paused" error, where prose outlived the runtime it described.
_MUTABLE_FACT_PATTERNS = (
    (r"\b(?:currently |now )?(?:on |at )?branch\b", "branch state belongs to Git"),
    (r"\bPR\s*#?\d+\b", "PR state belongs to Git"),
    (r"\bHEAD\b", "HEAD belongs to Git"),
    (r"\bcollector (?:is )?(?:running|paused|stopped|active)\b", "process state belongs to the runtime"),
    (r"\bwriter (?:is )?(?:running|paused|stopped|active|held)\b", "writer state belongs to the runtime"),
    (r"\b(?:as of|last updated|last run)\s+\d{4}-\d{2}-\d{2}", "timestamps go stale; point at the source"),
    (r"\b\d{1,3}(?:,\d{3})+\s+(?:rows|records|events|units)\b", "counts belong to the data artifact"),
)

# Sections a durable orientation summary should carry.
PROJECT_STATE_TOPICS = (
    "goal", "decision", "bottleneck", "evidence", "claim",
    "blocker", "next unknown", "gate",
)


@dataclass(frozen=True)
class StateWarning:
    line_number: int
    line: str
    reason: str


def project_state_warnings(text: str) -> List[StateWarning]:
    """Flag mutable facts frozen into durable prose.

    Advisory, not fatal: the point is to move the fact to its authoritative
    surface, not to fail a build over a sentence.
    """
    import re as _re

    warnings: List[StateWarning] = []
    in_fence = False
    for i, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        # Fenced examples and headings quote these facts deliberately.
        if in_fence or not stripped or stripped.startswith(("#", ">")):
            continue
        for pattern, reason in _MUTABLE_FACT_PATTERNS:
            if _re.search(pattern, stripped, _re.IGNORECASE):
                warnings.append(StateWarning(i, stripped[:100], reason))
                break
    return warnings


# --------------------------------------------------------------------------
# Derived-artifact reuse
# --------------------------------------------------------------------------
#
# Tenniskal replayed ~38k match events to produce a frozen 1,042-row evaluation
# artifact. A downstream Elo-vs-Kalshi comparison should read that artifact, not
# replay the history again because a fresh session started. Recomputation is
# warranted only when the upstream contract actually changed.


def contract_fingerprint(contract: Dict[str, Any]) -> str:
    """Stable hash of an upstream contract, so key order and prose do not matter."""
    import hashlib
    import json as _json

    blob = _json.dumps(contract or {}, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class DerivedArtifact:
    """An authoritative product of deterministic upstream work.

    ``upstream_contract`` is whatever must hold for the artifact to still answer
    the question: source dataset, target definition, filters, split, as-of date.
    """

    name: str
    upstream_contract: Dict[str, Any] = field(default_factory=dict)
    rows: Optional[int] = None
    path: str = ""

    @property
    def fingerprint(self) -> str:
        return contract_fingerprint(self.upstream_contract)


@dataclass(frozen=True)
class ReuseDecision:
    reuse: bool
    reason: str
    changed: Tuple[str, ...] = ()

    def __bool__(self) -> bool:
        return self.reuse


def artifact_reuse(
    artifact: Optional[DerivedArtifact],
    current_contract: Dict[str, Any],
    *,
    upstream_under_challenge: bool = False,
) -> ReuseDecision:
    """Reuse an authoritative derived artifact when its contract still holds.

    ``upstream_under_challenge`` is the one case where recomputation is right
    even with an unchanged contract: the mission is questioning how the artifact
    was built, so reading its output would beg the question.
    """
    if artifact is None:
        return ReuseDecision(False, "no derived artifact exists; compute it")
    if upstream_under_challenge:
        return ReuseDecision(
            False,
            f"the mission challenges how {artifact.name} was constructed; recompute rather than assume it",
        )
    changed = tuple(sorted(
        key for key in set(artifact.upstream_contract) | set(current_contract or {})
        if artifact.upstream_contract.get(key) != (current_contract or {}).get(key)
    ))
    if changed:
        return ReuseDecision(
            False,
            f"{artifact.name} is stale: " + ", ".join(changed) + " changed since it was built",
            changed,
        )
    rows = f" ({artifact.rows} rows)" if artifact.rows else ""
    return ReuseDecision(
        True,
        f"reuse {artifact.name}{rows}; the upstream contract is unchanged. "
        "A fresh session is not a reason to recompute.",
    )
