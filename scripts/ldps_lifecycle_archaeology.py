#!/usr/bin/env python3
"""Reconstruct the build order of a prediction system from git history.

Answers, for one repository: when did each lifecycle stage first appear, which
never appeared, where did the sequence double back, which modules were rewritten
most, and what was abandoned.

Two measurement hazards this script handles explicitly, both found in an earlier
OODA forensics pass:

  * BULK IMPORT. A commit that adds a large share of the corpus at once makes
    "first appearance" meaningless for every file inside it -- those files have
    one shared date, not an order. Such commits are detected and reported, and
    stages that first appear inside one are flagged UNRESOLVED rather than dated.
  * DESIGNED CHURN. State and status documents are rewritten by design, so a
    naive "most modified file" ranking just finds them. Rework is reported both
    naive and corrected.

Read-only: runs `git log` / `git show` against a checkout it never mutates.

Usage: python3 ldps_lifecycle_archaeology.py REPO [--out DIR] [--bulk-threshold 25]
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

# Ordered: first match wins, so the specific precedes the generic.
STAGE_RULES: list[tuple[str, str]] = [
    ("calibration",   r"calibrat"),
    ("backtesting",   r"backtest|walkforward|_replay|replay_|/pit_replay"),
    ("validation",    r"valid|verify|verif|honesty|placebo|_audit|audit_|stress_test|loso|sensitivity"),
    ("eval_metric",   r"scoring|score_|_score|evaluate_|metric"),
    ("monitoring",    r"monitor|drift|alert|recalibration_trigger|daily_runner|daily_orchestrator|live_refresh"),
    ("decision_surface", r"dashboard|live_card|picks_panel|execution_card|live_scanner|live_picks|report_"),
    ("portfolio_staking", r"portfolio|staking|bankroll|kelly|barbell|allocate|leverage"),
    ("models",        r"/modeling/|hypothesis_|system_factory|system_lib|ridge|classifier|ensemble|_model|discover|novelty|prim_search|tree_search|grid_search"),
    ("features",      r"feature|factor|transform|compute_|census|/eda/"),
    ("ingestion",     r"/ingestion/|fetch_|normalize_|refresh_|capture|build_master|build_historical|build_data_vault|run_pipeline|/pipeline/"),
    ("target_def",    r"target|label|outcome|settle"),
    ("baselines",     r"baseline|benchmark"),
    ("docs",          r"\.md$"),
    ("config",        r"\.ya?ml$|config|requirements|\.gitignore"),
    ("notebook",      r"\.ipynb$"),
]

# Coarse 3-way split for the composition question.
COMPOSITION = [
    ("evaluation", r"valid|verify|verif|honesty|placebo|_audit|audit_|backtest|walkforward|replay|calibrat|scoring|score_|loso|stress_test|sensitivity"),
    ("modeling",   r"/modeling/|hypothesis_|system_factory|system_lib|feature|factor|transform|discover|novelty|prim_search|tree_search|grid_search|/eda/"),
    ("scaffolding", r".*"),
]

DESIGNED_CHURN = re.compile(r"\.md$|state|status|log|readme|handoff|timeline|roadmap", re.I)
DATA_EXT = re.compile(r"\.(csv|json|parquet|sqlite|db|txt|bak.*|pyl)$", re.I)


def git(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args],
                          check=True, capture_output=True, text=True).stdout


def classify(path: str, rules) -> str:
    low = path.lower()
    for name, pat in rules:
        if re.search(pat, low):
            return name
    return "other"


def file_history(repo: Path) -> dict[str, dict]:
    """One pass over the whole log: first-add commit and modify-count per path.

    `--name-status` with `-m --first-parent` attributes merge content to the
    merge's first parent, so a file is not double counted by a merge commit."""
    out = git(repo, "log", "--reverse", "-m", "--first-parent",
              "--name-status", "--format=@@%H|%ct|%s")
    hist: dict[str, dict] = {}
    sha = ts = subject = None
    added_by: dict[str, list[str]] = defaultdict(list)
    for line in out.splitlines():
        if line.startswith("@@"):
            sha, ts, subject = line[2:].split("|", 2)
            continue
        if not line.strip() or sha is None:
            continue
        parts = line.split("\t")
        status, path = parts[0], parts[-1]
        rec = hist.setdefault(path, {
            "path": path, "first_sha": None, "first_ts": None, "first_subject": None,
            "n_commits": 0, "deleted_ts": None, "deleted_sha": None,
        })
        rec["n_commits"] += 1
        if status.startswith("A") and rec["first_sha"] is None:
            rec.update(first_sha=sha, first_ts=int(ts), first_subject=subject)
            added_by[sha].append(path)
        if status.startswith("D"):
            rec["deleted_ts"], rec["deleted_sha"] = int(ts), sha
        if status.startswith("R") and rec["first_sha"] is None:
            rec.update(first_sha=sha, first_ts=int(ts), first_subject=subject)
            added_by[sha].append(path)
    for rec in hist.values():
        rec["bulk_cohort_size"] = len(added_by.get(rec["first_sha"], []))
    return hist


def iso(ts) -> str:
    return dt.datetime.utcfromtimestamp(ts).strftime("%Y-%m-%d") if ts else ""


def build(repo: Path, bulk_threshold: int) -> dict:
    hist = file_history(repo)
    live = set(git(repo, "ls-files").split("\n")) - {""}

    for path, rec in hist.items():
        rec["stage"] = classify(path, STAGE_RULES)
        rec["composition"] = classify(path, COMPOSITION)
        rec["is_data"] = bool(DATA_EXT.search(path))
        rec["archived"] = "/archive/" in path.lower()
        rec["present_at_head"] = path in live
        rec["designed_churn"] = bool(DESIGNED_CHURN.search(path))
        rec["in_bulk_import"] = rec["bulk_cohort_size"] >= bulk_threshold

    # Stage first appearance, excluding data blobs (a stage is code/docs, not rows).
    stages: dict[str, dict] = {}
    for rec in hist.values():
        if rec["is_data"] or rec["first_ts"] is None:
            continue
        s = rec["stage"]
        cur = stages.get(s)
        if cur is None or rec["first_ts"] < cur["first_ts"]:
            stages[s] = {
                "stage": s, "first_ts": rec["first_ts"], "first_date": iso(rec["first_ts"]),
                "first_sha": rec["first_sha"][:9], "cohort_size": rec["bulk_cohort_size"],
                "resolved": not rec["in_bulk_import"],
            }
    for s in stages:
        stages[s]["n_files"] = sum(
            1 for r in hist.values() if r["stage"] == s and not r["is_data"])

    # A stage whose only filename matches were claimed by an earlier rule is
    # SHADOWED, not absent -- report the difference rather than assert absence.
    shadowed: dict[str, list[str]] = {}
    for name, pat in STAGE_RULES:
        if name in stages:
            continue
        hits = [r["path"] for r in hist.values()
                if not r["is_data"] and re.search(pat, r["path"].lower())]
        if hits:
            shadowed[name] = [
                {"dir": h.rsplit("/", 1)[0], "claimed_by": classify(h, STAGE_RULES)}
                for h in sorted(hits)
            ]

    bulk = Counter()
    for rec in hist.values():
        if rec["in_bulk_import"] and rec["first_sha"]:
            bulk[(rec["first_sha"][:9], iso(rec["first_ts"]))] = rec["bulk_cohort_size"]

    rework_all = sorted((r for r in hist.values() if not r["is_data"]),
                        key=lambda r: -r["n_commits"])
    rework_corr = [r for r in rework_all if not r["designed_churn"]]

    abandoned = [r for r in hist.values()
                 if (r["deleted_ts"] and not r["present_at_head"]) or r["archived"]]

    comp = Counter()
    comp_files = Counter()
    for path in live:
        rec = hist.get(path)
        if rec is None or rec["is_data"]:
            continue
        try:
            n = sum(1 for _ in (repo / path).open(encoding="utf-8", errors="ignore"))
        except OSError:
            n = 0
        comp[rec["composition"]] += n
        comp_files[rec["composition"]] += 1

    return {
        "repo_head": git(repo, "rev-parse", "HEAD").strip(),
        "n_commits": int(git(repo, "rev-list", "--count", "HEAD").strip()),
        "n_files_head": len(live),
        "bulk_imports": [{"sha": k[0], "date": k[1], "files_added": v}
                         for k, v in sorted(bulk.items(), key=lambda x: -x[1])],
        "stages": sorted(stages.values(), key=lambda s: s["first_ts"]),
        "stages_absent": [s for s, _ in STAGE_RULES
                          if s not in stages and s not in shadowed],
        "stages_shadowed": shadowed,
        "rework_naive": [{"dir": r["path"].rsplit("/", 1)[0], "n_commits": r["n_commits"],
                          "designed_churn": r["designed_churn"]} for r in rework_all[:10]],
        "rework_corrected": [{"dir": r["path"].rsplit("/", 1)[0], "n_commits": r["n_commits"],
                              "stage": r["stage"]} for r in rework_corr[:10]],
        "abandoned": {
            "n_files": len(abandoned),
            "n_archived_in_place": sum(1 for r in abandoned if r["archived"]),
            "n_deleted": sum(1 for r in abandoned if not r["archived"]),
            "by_stage": dict(Counter(r["stage"] for r in abandoned)),
            "by_dir": dict(Counter(r["path"].rsplit("/", 1)[0] for r in abandoned).most_common(8)),
        },
        "composition_lines": dict(comp),
        "composition_files": dict(comp_files),
        "_hist": hist,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--out", default=".")
    ap.add_argument("--bulk-threshold", type=int, default=25)
    a = ap.parse_args()
    res = build(Path(a.repo).resolve(), a.bulk_threshold)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    hist = res.pop("_hist")
    with (out / "ldps_stage_timeline.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["stage", "first_date", "first_sha", "resolved", "cohort_size", "n_files"])
        for s in res["stages"]:
            w.writerow([s["stage"], s["first_date"], s["first_sha"],
                        s["resolved"], s["cohort_size"], s["n_files"]])
        for s in res["stages_absent"]:
            w.writerow([s, "", "", "ABSENT", "", 0])
    (out / "ldps_archaeology.json").write_text(json.dumps(res, indent=2) + "\n", encoding="utf-8")
    print(f"{res['n_commits']} commits, {res['n_files_head']} files at HEAD")
    print(f"bulk imports (>= {a.bulk_threshold} files): {len(res['bulk_imports'])}")
    print(f"stages dated: {len(res['stages'])}  absent: {res['stages_absent']}")
    for k, v in res["stages_shadowed"].items():
        print(f"  SHADOWED {k}: {len(v)} filename match(es), claimed by "
              f"{sorted({x['claimed_by'] for x in v})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
