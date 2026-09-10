"""Environment preflight.

A whole remote Crypto mission was implemented before anyone checked whether the
environment held the operator-host snapshot it needed. This module makes that
check cheap and mandatory for environment-dependent missions, so the failure is
caught before the expensive work rather than after it.
"""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence

REQUIREMENT_KINDS = ("path", "command", "env", "host_service")


@dataclass(frozen=True)
class Requirement:
    """One thing a mission needs from the environment it will run in."""

    kind: str
    value: str
    why: str = ""

    def __post_init__(self) -> None:
        if self.kind not in REQUIREMENT_KINDS:
            raise ValueError(f"unknown requirement kind: {self.kind!r}")


@dataclass(frozen=True)
class RequirementResult:
    requirement: Requirement
    satisfied: bool
    detail: str = ""


@dataclass(frozen=True)
class PreflightReport:
    results: tuple
    route_to: Optional[str] = None

    @property
    def satisfied(self) -> bool:
        return all(r.satisfied for r in self.results)

    @property
    def missing(self) -> tuple:
        return tuple(r for r in self.results if not r.satisfied)

    def handoff(self) -> str:
        """A concrete route, not a shrug."""
        if self.satisfied:
            return "environment satisfies all declared requirements"
        names = ", ".join(f"{r.requirement.kind}:{r.requirement.value}" for r in self.missing)
        where = self.route_to or "the environment that holds them"
        return (
            f"environment is missing {names}. "
            f"Code may be written here, but data-dependent execution must run on {where}. "
            "Stop before data-dependent implementation or evaluation and route the mission."
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "satisfied": self.satisfied,
            "route_to": self.route_to,
            "missing": [
                {"kind": r.requirement.kind, "value": r.requirement.value, "why": r.requirement.why,
                 "detail": r.detail}
                for r in self.missing
            ],
            "handoff": self.handoff(),
        }


def _check(req: Requirement) -> RequirementResult:
    if req.kind == "path":
        p = Path(os.path.expanduser(os.path.expandvars(req.value)))
        ok = p.exists()
        return RequirementResult(req, ok, "present" if ok else "not found")
    if req.kind == "command":
        found = shutil.which(req.value)
        return RequirementResult(req, bool(found), found or "not on PATH")
    if req.kind == "env":
        ok = bool(os.environ.get(req.value))
        return RequirementResult(req, ok, "set" if ok else "unset or empty")
    # host_service cannot be probed portably; it must be asserted by the operator.
    return RequirementResult(req, False, "host service cannot be verified from this environment")


def parse_requirements(raw: Iterable[Any]) -> List[Requirement]:
    out: List[Requirement] = []
    for item in raw or ():
        if isinstance(item, Requirement):
            out.append(item)
        elif isinstance(item, dict):
            out.append(Requirement(kind=item.get("kind", "path"), value=item["value"],
                                   why=item.get("why", "")))
        elif isinstance(item, str) and ":" in item:
            kind, _, value = item.partition(":")
            out.append(Requirement(kind=kind.strip(), value=value.strip()))
        else:
            raise ValueError(f"cannot parse requirement: {item!r}")
    return out


def preflight(requirements: Iterable[Any], *, route_to: Optional[str] = None) -> PreflightReport:
    """Check declared requirements against the environment actually running.

    Returns a report; it never raises on an unsatisfied environment, because the
    correct response is to route the mission, not to crash.
    """
    reqs = parse_requirements(requirements)
    return PreflightReport(tuple(_check(r) for r in reqs), route_to=route_to)


def requires_preflight(mission: Dict[str, Any]) -> bool:
    """True when a mission declares any environment dependency."""
    return bool(mission.get("environment_requirements"))
