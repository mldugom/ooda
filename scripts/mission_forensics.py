#!/usr/bin/env python3
"""Reconstruct an OODA mission timeline from git history.

The mission artifacts themselves carry no usable timing: work orders record a
date-only `created`, traces record no completion timestamp, and no telemetry
ledger exists. Git commit metadata is therefore the only timeline available.

Every column below is DERIVED from commit metadata and numstat. No artifact
prose (objectives, verification text, findings) is read or emitted, and file
paths are aggregated to their top-level directory only.

Read-only: runs `git log` / `git diff` against a checkout it never mutates.

Usage:
    python3 mission_forensics.py REPO [--out DIR]
"""
from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

WO_GLOB = ".ooda/work-orders/*.json"
TRACE_GLOB = ".ooda/traces/*.json"
REWORK_WINDOW_HOURS = 72


def git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True, capture_output=True, text=True,
    ).stdout


def added_commit(repo: Path, path: str) -> dict | None:
    """Earliest commit that ADDED this path. Author and committer dates are both
    kept: a divergence means the history was rebased or cherry-picked, and the
    committer clock is then not a record of when the work happened."""
    out = git(repo, "log", "--diff-filter=A", "--format=%H%x1f%ct%x1f%at", "--", path).strip()
    if not out:
        return None
    sha, ctime, atime = out.splitlines()[-1].split("\x1f")
    return {"sha": sha, "commit_time": int(ctime), "author_time": int(atime)}


def tracked(repo: Path, pattern: str) -> list[str]:
    return [p for p in git(repo, "ls-files", pattern).splitlines() if p.strip()]


def read_json(repo: Path, path: str) -> dict:
    try:
        return json.loads((repo / path).read_text(encoding="utf-8"))
    except Exception:
        return {}


def commit_delta(repo: Path, sha: str) -> dict:
    """Footprint of a single commit, excluding OODA's own bookkeeping.

    Scope is measured on the commit that INTRODUCES a mission's artifacts, not
    across a work-order..trace range: in this corpus that range is empty for
    20/22 missions because both files arrive in one commit. A merge commit is
    diffed against its first parent."""
    out = git(repo, "show", "--numstat", "--format=", "-m", "--first-parent", sha)
    files = ins = dele = 0
    dirs: set[str] = set()
    paths: set[str] = set()
    for line in out.splitlines():
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        a, d, path = parts
        if path.startswith(".ooda/"):
            continue
        files += 1
        ins += int(a) if a.isdigit() else 0
        dele += int(d) if d.isdigit() else 0
        dirs.add(path.split("/")[0])
        paths.add(path)
    return {"files": files, "insertions": ins, "deletions": dele, "dirs": dirs, "paths": paths}


def build(repo: Path) -> dict:
    work_orders, traces = {}, {}

    for path in tracked(repo, WO_GLOB):
        data = read_json(repo, path)
        wid = data.get("id") or Path(path).stem
        commit = added_commit(repo, path)
        work_orders[wid] = {
            "mission_id": wid,
            "wo_path": path,
            "wo_commit": commit,
            "lens_count": len(data.get("lenses") or []),
            "claim_level": data.get("claim_level"),
            "role": data.get("role"),
            "has_decision_served": bool(data.get("decision_served")),
        }

    for path in tracked(repo, TRACE_GLOB):
        data = read_json(repo, path)
        # `work_order_id` is the schema field; `id` is what hand-authored
        # traces in the wild actually use. Fall back to the filename.
        wid = data.get("work_order_id") or data.get("id") or Path(path).stem
        traces[wid] = {
            "trace_path": path,
            "trace_commit": added_commit(repo, path),
            "result_state": (data.get("result") or {}).get("state") or data.get("state"),
            "trace_key_used": "work_order_id" if data.get("work_order_id")
                              else ("id" if data.get("id") else "filename"),
        }

    missions = []
    for wid, wo in work_orders.items():
        tr = traces.get(wid, {})
        wc, tc = wo["wo_commit"], tr.get("trace_commit")
        elapsed = None
        same_commit = None
        if wc and tc:
            elapsed = round((tc["commit_time"] - wc["commit_time"]) / 3600.0, 2)
            same_commit = wc["sha"] == tc["sha"]
        delta = commit_delta(repo, wc["sha"]) if wc else \
            {"files": None, "insertions": None, "deletions": None, "dirs": set(), "paths": set()}
        missions.append({
            **{k: v for k, v in wo.items() if k != "wo_commit"},
            "wo_sha": wc["sha"][:9] if wc else None,
            "wo_commit_time": wc["commit_time"] if wc else None,
            "wo_rebased": (wc["commit_time"] != wc["author_time"]) if wc else None,
            "trace_sha": tc["sha"][:9] if tc else None,
            "trace_commit_time": tc["commit_time"] if tc else None,
            "has_trace": bool(tc),
            "same_commit_as_trace": same_commit,
            "elapsed_hours": elapsed,
            "result_state": tr.get("result_state"),
            "files_changed": delta["files"],
            "insertions": delta["insertions"],
            "deletions": delta["deletions"],
            "top_level_dirs": "|".join(sorted(delta["dirs"])),
            "_paths": delta["paths"],
        })

    missions.sort(key=lambda m: (m["wo_commit_time"] is None, m["wo_commit_time"] or 0))
    prev = None
    for i, m in enumerate(missions, 1):
        m["seq"] = i
        m["gap_hours_since_prev"] = (
            round((m["wo_commit_time"] - prev) / 3600.0, 2)
            if prev is not None and m["wo_commit_time"] else None
        )
        prev = m["wo_commit_time"] or prev

    # Rework: a file touched inside the range of two missions whose work orders
    # were committed within REWORK_WINDOW_HOURS of each other.
    touched: dict[str, list[dict]] = defaultdict(list)
    for m in missions:
        for p in m["_paths"]:
            touched[p].append(m)
    # Missions backfilled in one commit share an indivisible footprint, so a
    # file they all "touch" is one edit, not rework. Only pairs introduced by
    # DIFFERENT commits count.
    rework = []
    for path, ms in touched.items():
        if len(ms) < 2:
            continue
        pairs = [
            (a["mission_id"], b["mission_id"])
            for i, a in enumerate(ms) for b in ms[i + 1:]
            if a["wo_sha"] != b["wo_sha"]
            and a["wo_commit_time"] and b["wo_commit_time"]
            and abs(a["wo_commit_time"] - b["wo_commit_time"]) <= REWORK_WINDOW_HOURS * 3600
        ]
        if pairs:
            rework.append({
                "dir": path.split("/")[0],
                "n_distinct_commits": len({m["wo_sha"] for m in ms}),
                "n_missions": len(ms),
                "n_pairs": len(pairs),
            })

    orphans = [
        {"trace_key": k, "trace_key_used": v["trace_key_used"],
         "trace_sha": (v["trace_commit"] or {}).get("sha", "")[:9]}
        for k, v in traces.items() if k not in work_orders
    ]

    for m in missions:
        del m["_paths"]
    return {
        "repo_head": git(repo, "rev-parse", "HEAD").strip(),
        "n_work_orders": len(work_orders),
        "n_traces": len(traces),
        "missions": missions,
        "orphan_traces": orphans,
        "rework": sorted(rework, key=lambda r: -r["n_missions"]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--out", default=".")
    a = ap.parse_args()
    result = build(Path(a.repo).resolve())
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)

    cols = ["seq", "mission_id", "wo_sha", "trace_sha", "has_trace", "same_commit_as_trace",
            "elapsed_hours", "gap_hours_since_prev",
            "files_changed", "insertions", "deletions", "top_level_dirs",
            "lens_count", "claim_level", "role", "has_decision_served", "result_state",
            "wo_rebased", "wo_commit_time", "trace_commit_time"]
    with (out / "mission_timeline.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(result["missions"])
    (out / "mission_forensics.json").write_text(
        json.dumps({k: v for k, v in result.items() if k != "missions"}, indent=2) + "\n",
        encoding="utf-8")
    print(f"{result['n_work_orders']} work orders, {result['n_traces']} traces -> {out}/mission_timeline.csv")
    print(f"orphan traces: {len(result['orphan_traces'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
