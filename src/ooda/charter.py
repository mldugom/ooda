"""Prediction charter -- the target freeze for predictive science.

Crypto and Tenniskal both drifted because the research objective was implicit
and could move quietly when a model disappointed. A charter makes the objective
explicit and small, and makes changing it an event rather than an edit.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple

SCHEMA = "ooda/prediction-charter/v1"

# Deliberately nine fields. Enough to stop goalpost drift, small enough to write
# before modelling rather than instead of it.
REQUIRED_FIELDS = (
    "decision",           # repeated action we are trying to improve
    "target",             # exactly what outcome is predicted
    "why_target_matters", # link from outcome back to the decision
    "decision_time",      # what information is legally available then
    "baseline",           # the simple thing that must be beaten
    "primary_metrics",    # how success is judged
    "holdout",            # what may never be tuned against
    "stop_rule",          # when to stop modelling and reconsider
    "resource_budget",    # expected ceiling
)

OPTIONAL_FIELDS = ("model_budget", "prospective", "notes")

# Fields whose change alters what "success" means. Changing any of these is a
# re-orientation, not an edit.
FROZEN_FIELDS = ("decision", "target", "decision_time", "baseline", "primary_metrics", "holdout")


def validate_charter(data: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    if data.get("schema") != SCHEMA:
        errors.append(f"schema must be {SCHEMA}")
    for key in REQUIRED_FIELDS:
        if not data.get(key):
            errors.append(f"{key} is required")
    metrics = data.get("primary_metrics")
    if metrics is not None and not isinstance(metrics, (list, tuple, str)):
        errors.append("primary_metrics must be a string or list")
    return errors


def _frozen_view(data: Dict[str, Any]) -> Dict[str, Any]:
    return {k: data.get(k) for k in FROZEN_FIELDS}


def charter_fingerprint(data: Dict[str, Any]) -> str:
    """Stable hash of the frozen fields only, so prose edits do not look like drift."""
    blob = json.dumps(_frozen_view(data), sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class CharterChange:
    changed: Tuple[str, ...]
    requires_reorientation: bool
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "changed": list(self.changed),
            "requires_reorientation": self.requires_reorientation,
            "reason": self.reason,
        }


def diff_charter(old: Dict[str, Any], new: Dict[str, Any]) -> CharterChange:
    """Detect goalpost movement.

    Any frozen-field change is a re-orientation gate. It is not forbidden --
    evidence legitimately changes targets -- but it must be decided, not slipped.
    """
    changed = tuple(k for k in FROZEN_FIELDS if old.get(k) != new.get(k))
    if not changed:
        return CharterChange((), False, "no frozen field changed")
    return CharterChange(
        changed,
        True,
        "changing " + ", ".join(changed) + " redefines success; record an explicit re-orientation "
        "decision with the evidence that motivated it. A disappointing model is not evidence.",
    )


def target_change_is_reorientation(old: Dict[str, Any], new: Dict[str, Any]) -> bool:
    return diff_charter(old, new).requires_reorientation


def new_charter(**fields: Any) -> Dict[str, Any]:
    data: Dict[str, Any] = {"schema": SCHEMA}
    data.update({k: v for k, v in fields.items() if v is not None})
    return data
