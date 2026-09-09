import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import mission_economics as econ
from ooda.telemetry_ledger import record_snapshot
from ooda.xai_usage import LOCAL_DERIVED, PROVIDER_REPORTED, UNAVAILABLE


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data), encoding="utf-8")


class _RepoBuilder:
    """Small helper for real-shaped .ooda fixtures across tests."""

    def __init__(self, root: Path, name: str = "demo"):
        self.repo = root / name
        (self.repo / ".ooda" / "work-orders").mkdir(parents=True, exist_ok=True)
        (self.repo / ".ooda" / "traces").mkdir(parents=True, exist_ok=True)

    def work_order(self, mission_id: str, created_at: str) -> "_RepoBuilder":
        _write_json(
            self.repo / ".ooda" / "work-orders" / f"{mission_id}.json",
            {"id": mission_id, "created_at": created_at},
        )
        return self

    def trace(self, mission_id: str, completed_at: str, *, state: str = "completed", provider: str = "grok") -> "_RepoBuilder":
        _write_json(
            self.repo / ".ooda" / "traces" / f"{mission_id}.json",
            {"work_order_id": mission_id, "completed_at": completed_at, "result": {"state": state}, "provider": provider},
        )
        return self

    def snapshot(self, *, session_id: str, cost: float, at: str) -> "_RepoBuilder":
        record_snapshot(
            self.repo,
            provider="grok",
            model="Grok 4.6",
            session_id=session_id,
            cumulative_session_cost_usd=cost,
            cumulative_session_cost_provenance=PROVIDER_REPORTED,
        )
        self._retime_last_event(at)
        return self

    def _retime_last_event(self, at: str) -> None:
        path = econ_ledger_path(self.repo)
        lines = path.read_text(encoding="utf-8").splitlines()
        record = json.loads(lines[-1])
        record["at"] = at
        lines[-1] = json.dumps(record, sort_keys=True)
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def econ_ledger_path(repo: Path) -> Path:
    from ooda.telemetry_ledger import ledger_path

    return ledger_path(repo)


class MissionLifecycleTests(unittest.TestCase):
    def test_mission_lifecycle_start_and_end(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z").trace("M1", "2026-09-01T10:20:00Z")
            missions = econ.mission_lifecycle(b.repo)
        self.assertEqual(len(missions), 1)
        self.assertEqual(missions[0]["created_at"], "2026-09-01T10:00:00Z")
        self.assertEqual(missions[0]["completed_at"], "2026-09-01T10:20:00Z")

    def test_completed_mission_gets_elapsed_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z").trace("M1", "2026-09-01T10:20:00Z")
            missions = econ.mission_lifecycle(b.repo)
        self.assertAlmostEqual(missions[0]["elapsed_minutes"], 20.0)

    def test_open_mission_has_no_elapsed_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z")
            missions = econ.mission_lifecycle(b.repo)
        self.assertIsNone(missions[0]["elapsed_minutes"])
        self.assertIsNone(missions[0]["completed_at"])


class MissionSpendAttributionTests(unittest.TestCase):
    def test_mission_spend_is_local_derived_from_ledger_window(self):
        """Reproduces the dogfood scenario: a fast mission whose TRACE is
        already written before the ledger records the delta, so the live
        'one open work order' rule alone would see zero open missions."""
        with tempfile.TemporaryDirectory() as tmp:
            b = (
                _RepoBuilder(Path(tmp))
                .work_order("M1", "2026-09-01T10:00:00Z")
                .trace("M1", "2026-09-01T10:05:00Z")
            )
            # Snapshot arrives AFTER the trace already exists — the race that
            # broke the live attribution rule.
            b.snapshot(session_id="s1", cost=2.527, at="2026-09-01T10:04:00Z")

            report = econ.mission_economics_report(b.repo)

        self.assertEqual(len(report), 1)
        self.assertAlmostEqual(report[0]["attributed_spend_usd"], 2.527)
        self.assertEqual(report[0]["spend_provenance"], LOCAL_DERIVED)

    def test_mission_spend_never_labeled_exact_api(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z").trace("M1", "2026-09-01T10:05:00Z")
            b.snapshot(session_id="s1", cost=1.0, at="2026-09-01T10:02:00Z")
            report = econ.mission_economics_report(b.repo)
        self.assertNotEqual(report[0]["spend_provenance"], "EXACT_API")

    def test_no_attribution_when_multiple_missions_overlap(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = (
                _RepoBuilder(Path(tmp))
                .work_order("M1", "2026-09-01T10:00:00Z")
                .trace("M1", "2026-09-01T10:30:00Z")
                .work_order("M2", "2026-09-01T10:10:00Z")
                .trace("M2", "2026-09-01T10:40:00Z")
            )
            # This event's timestamp falls inside BOTH windows.
            b.snapshot(session_id="s1", cost=1.0, at="2026-09-01T10:20:00Z")

            attributed = econ.attribute_events(b.repo)

        self.assertNotIn("M1", attributed)
        self.assertNotIn("M2", attributed)
        self.assertAlmostEqual(attributed["__unattributed__"]["spend_usd"], 1.0)

    def test_unattributed_bucket_remains_honest(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            (repo / ".ooda" / "traces").mkdir(parents=True)
            record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.5, cumulative_session_cost_provenance=PROVIDER_REPORTED,
            )
            attributed = econ.attribute_events(repo)
        self.assertAlmostEqual(attributed["__unattributed__"]["spend_usd"], 0.5)
        self.assertIn("s1", attributed["__unattributed__"]["by_session"])

    def test_missing_provider_telemetry_gives_none_not_zero(self):
        """A completed mission with no ledger events at all in its window
        must not be reported as costing $0 — that would be a manufactured
        number, not an honest 'no telemetry' state."""
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z").trace("M1", "2026-09-01T10:05:00Z")
            report = econ.mission_economics_report(b.repo)
        self.assertIsNone(report[0]["attributed_spend_usd"])
        self.assertEqual(report[0]["spend_provenance"], UNAVAILABLE)

    def test_no_historical_mtime_inference(self):
        """A work order/trace pair with no created_at/completed_at fields at
        all must not produce a mission point, even though the files
        themselves have filesystem mtimes OODA could have (but must not)
        used."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            (repo / ".ooda" / "traces").mkdir(parents=True)
            _write_json(repo / ".ooda" / "work-orders" / "M1.json", {"id": "M1"})
            _write_json(repo / ".ooda" / "traces" / "M1.json", {"work_order_id": "M1", "result": {"state": "completed"}})
            report = econ.mission_economics_report(repo)
        self.assertIsNone(report[0]["elapsed_minutes"])
        self.assertIsNone(report[0]["attributed_spend_usd"])

    def test_duplicate_telemetry_events_do_not_inflate_mission_spend(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z").trace("M1", "2026-09-01T10:30:00Z")
            for _ in range(3):
                record_snapshot(
                    b.repo, provider="grok", model="Grok 4.6", session_id="s1",
                    cumulative_session_cost_usd=1.0, cumulative_session_cost_provenance=PROVIDER_REPORTED,
                )
            b._retime_last_event("2026-09-01T10:10:00Z")
            report = econ.mission_economics_report(b.repo)
        self.assertAlmostEqual(report[0]["attributed_spend_usd"], 1.0)

    def test_session_reset_within_mission_window_still_sums_correctly(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z").trace("M1", "2026-09-01T10:30:00Z")
            b.snapshot(session_id="s1", cost=0.5, at="2026-09-01T10:05:00Z")
            b.snapshot(session_id="s1", cost=0.2, at="2026-09-01T10:10:00Z")  # reset: treated as fresh delta
            report = econ.mission_economics_report(b.repo)
        self.assertAlmostEqual(report[0]["attributed_spend_usd"], 0.7)


class CostGuzzlerTests(unittest.TestCase):
    def test_completed_mission_recovered_from_unattributed(self):
        """The exact dogfood bug: attribution must land on the mission, not
        session/unattributed, once the mission's window is known."""
        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp)).work_order("M1", "2026-09-01T10:00:00Z").trace("M1", "2026-09-01T10:05:00Z")
            b.snapshot(session_id="s1", cost=2.527, at="2026-09-01T10:04:00Z")
            rows = econ.cost_guzzlers(b.repo)
        self.assertEqual(rows[0]["label"], "M1")
        self.assertAlmostEqual(rows[0]["spend_usd"], 2.527)

    def test_open_mission_still_attributed_live(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            (repo / ".ooda" / "traces").mkdir(parents=True)
            _write_json(repo / ".ooda" / "work-orders" / "validator.json", {"id": "validator"})
            record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.83, cumulative_session_cost_provenance=PROVIDER_REPORTED,
            )
            rows = econ.cost_guzzlers(repo)
        self.assertEqual(rows[0]["label"], "validator")


class RollupTests(unittest.TestCase):
    def test_project_rollup_date_windows(self):
        import datetime as dt

        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            (repo / ".ooda" / "traces").mkdir(parents=True)
            now = dt.datetime(2026, 9, 9, 12, 0, tzinfo=dt.timezone.utc)
            record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=1.0, cumulative_session_cost_provenance=PROVIDER_REPORTED,
            )
            b = _RepoBuilder.__new__(_RepoBuilder)
            b.repo = repo
            b._retime_last_event("2026-09-09T09:00:00Z")  # today

            record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s2",
                cumulative_session_cost_usd=2.0, cumulative_session_cost_provenance=PROVIDER_REPORTED,
            )
            b._retime_last_event("2026-09-03T09:00:00Z")  # within 7d, not today

            record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s3",
                cumulative_session_cost_usd=3.0, cumulative_session_cost_provenance=PROVIDER_REPORTED,
            )
            b._retime_last_event("2026-08-01T09:00:00Z")  # older than 30d

            roll = econ.project_rollup(repo, now=now)

        self.assertAlmostEqual(roll["today_usd"], 1.0)
        self.assertAlmostEqual(roll["last_7d_usd"], 3.0)
        self.assertAlmostEqual(roll["all_time_usd"], 6.0)
        self.assertEqual(roll["provenance"], LOCAL_DERIVED)

    def test_portfolio_rollup_sums_across_projects(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("tenniskal", "crypto-innout"):
                repo = root / name
                (repo / ".ooda" / "work-orders").mkdir(parents=True)
                (repo / ".ooda" / "traces").mkdir(parents=True)
                _write_json(repo / ".ooda" / "project.json", {"project_id": name})
                record_snapshot(
                    repo, provider="grok", model="Grok 4.6", session_id="s1",
                    cumulative_session_cost_usd=1.5, cumulative_session_cost_provenance=PROVIDER_REPORTED,
                )
            roll = econ.portfolio_rollup(root)
        self.assertAlmostEqual(roll["total_usd"], 3.0)
        self.assertEqual(len(roll["projects"]), 2)

    def test_portfolio_rollup_no_data_is_unavailable_not_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "empty-project"
            (repo / ".ooda").mkdir(parents=True)
            _write_json(repo / ".ooda" / "project.json", {"project_id": "empty-project"})
            roll = econ.portfolio_rollup(root)
        self.assertEqual(roll["provenance"], UNAVAILABLE)
        self.assertFalse(roll["has_data"])


class FeedbackEfficiencyChartTests(unittest.TestCase):
    def _project(self, repo: Path) -> dict:
        return {"repo": repo, "objective": "x", "objective_ladder": [], "timeline": []}

    def test_hidden_below_three_valid_points(self):
        from ooda.control_room import _efficiency_chart

        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp))
            for i in range(2):
                mid = f"M{i}"
                b.work_order(mid, f"2026-09-0{i+1}T10:00:00Z").trace(mid, f"2026-09-0{i+1}T10:20:00Z")
                b.snapshot(session_id=f"s{i}", cost=1.0, at=f"2026-09-0{i+1}T10:10:00Z")
            html = _efficiency_chart(self._project(b.repo))
        self.assertIn("Not enough recorded mission economics", html)

    def test_appears_at_three_ledger_derived_points_without_manual_trace_cost(self):
        from ooda.control_room import _efficiency_chart

        with tempfile.TemporaryDirectory() as tmp:
            b = _RepoBuilder(Path(tmp))
            for i in range(3):
                mid = f"M{i}"
                b.work_order(mid, f"2026-09-0{i+1}T10:00:00Z").trace(mid, f"2026-09-0{i+1}T10:20:00Z")
                b.snapshot(session_id=f"s{i}", cost=1.0, at=f"2026-09-0{i+1}T10:10:00Z")
            html = _efficiency_chart(self._project(b.repo))
        self.assertIn("efficiency-chart", html)
        self.assertIn("LOCAL_DERIVED", html)


if __name__ == "__main__":
    unittest.main()
