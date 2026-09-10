"""Environment preflight and execution locality.

A whole remote Crypto mission was implemented before anyone checked whether the
environment held the operator-host snapshot it needed. This module makes that
check cheap and mandatory for environment-dependent missions, so the failure is
caught before the expensive work rather than after it.

It also answers the follow-up question, which is routing rather than blocking:
data stays where it lives, code moves to the data, and only compact evidence
comes back. A remote agent that cannot reach the authoritative snapshot may still
write and test the deterministic code; it just must not pretend to evaluate
against data it cannot see.
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
    at: str = ""  # authoritative location, when it is not this environment

    def __post_init__(self) -> None:
        if self.kind not in REQUIREMENT_KINDS:
            raise ValueError(f"unknown requirement kind: {self.kind!r}")

    @property
    def label(self) -> str:
        return f"{self.kind}:{self.value}"


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
                                   why=item.get("why", ""), at=item.get("at", "")))
        elif isinstance(item, str) and ":" in item:
            kind, _, rest = item.partition(":")
            # "path:/data/tape.sqlite@operator host" -- the location is part of
            # the requirement, so a mission can declare it without a dict.
            value, sep, at = rest.partition("@")
            out.append(Requirement(kind=kind.strip(), value=value.strip(),
                                   at=at.strip() if sep else ""))
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


# --------------------------------------------------------------------------
# Execution locality
# --------------------------------------------------------------------------

HERE = "this environment"


@dataclass(frozen=True)
class ExecutionPlan:
    """Where the deterministic part of a mission should actually run.

    Not a scheduler and not an RPC layer -- it decides a location and names the
    command, and something else runs it.
    """

    report: PreflightReport
    run_at: str
    entry_point: str = ""
    result_artifact: str = ""

    @property
    def runs_here(self) -> bool:
        return self.run_at == HERE

    @property
    def code_work_allowed(self) -> bool:
        """Writing and testing deterministic code never needs the real data.

        This is the half that stops a routing decision from reading as a research
        block: fixtures are enough to build and test the entry point.
        """
        return True

    @property
    def data_work_allowed_here(self) -> bool:
        return self.report.satisfied

    def summary(self) -> str:
        if self.runs_here:
            base = "deterministic execution may run here; all required resources are present"
        else:
            missing = ", ".join(r.requirement.label for r in self.report.missing)
            base = (
                f"deterministic execution must run at {self.run_at} — {missing} is not reachable here. "
                "Code may be written and tested here against fixtures; real evaluation may not."
            )
        if self.entry_point:
            base += f"\nRun: {self.entry_point}"
        if self.result_artifact:
            base += f"\nReturn only: {self.result_artifact}"
        return base

    def to_dict(self) -> Dict[str, Any]:
        return {
            "required": [r.requirement.label for r in self.report.results],
            "authoritative_location": {
                r.requirement.label: (r.requirement.at or HERE) for r in self.report.results
            },
            "available_here": self.report.satisfied,
            "run_at": self.run_at,
            "code_work_allowed_here": self.code_work_allowed,
            "data_work_allowed_here": self.data_work_allowed_here,
            "entry_point": self.entry_point,
            "result_artifact": self.result_artifact,
        }


def plan_execution(
    requirements: Iterable[Any],
    *,
    entry_point: str = "",
    result_artifact: str = "",
    route_to: Optional[str] = None,
) -> ExecutionPlan:
    """Decide where deterministic computation should run.

    When everything a mission needs is present, it runs here. When it is not, the
    plan names the authoritative location declared on the missing requirement --
    so the answer is a route, never a blanket stop.
    """
    report = preflight(requirements, route_to=route_to)
    if report.satisfied:
        run_at = HERE
    else:
        declared = [r.requirement.at for r in report.missing if r.requirement.at]
        run_at = declared[0] if declared else (route_to or "the environment that holds the data")
    return ExecutionPlan(
        report=report,
        run_at=run_at,
        entry_point=entry_point,
        result_artifact=result_artifact,
    )
