import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import telemetry_ledger as ledger
from ooda.xai_usage import EXACT_API, LOCAL_DERIVED, UNAVAILABLE


class TelemetryLedgerTests(unittest.TestCase):
    def _repo_with_open_mission(self, root: Path, mission_id: str = "M1") -> Path:
        repo = root / "demo"
        (repo / ".ooda" / "work-orders").mkdir(parents=True)
        (repo / ".ooda" / "traces").mkdir(parents=True)
        (repo / ".ooda" / "work-orders" / f"{mission_id}.json").write_text(
            json.dumps({"id": mission_id}), encoding="utf-8"
        )
        return repo

    def test_first_snapshot_records_full_cost_as_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp))
            ledger.record_snapshot(
                repo,
                provider="grok",
                model="Grok 4.6",
                session_id="s1",
                cumulative_session_cost_usd=0.10,
                cumulative_session_cost_provenance=EXACT_API,
                context_used=1000,
                session_input_tokens=800,
                session_output_tokens=200,
            )
            events = ledger.read_events(repo)

        self.assertEqual(len(events), 1)
        self.assertAlmostEqual(events[0]["delta_cost_usd"], 0.10)
        self.assertEqual(events[0]["delta_cost_provenance"], LOCAL_DERIVED)
        self.assertEqual(events[0]["work_order_id"], "M1")
        self.assertEqual(events[0]["attribution"], "mission")

    def test_session_accumulation_produces_positive_deltas_between_snapshots(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp))
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.10, cumulative_session_cost_provenance=EXACT_API,
            )
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.37, cumulative_session_cost_provenance=EXACT_API,
            )
            events = ledger.read_events(repo)

        self.assertEqual(len(events), 2)
        self.assertAlmostEqual(events[0]["delta_cost_usd"], 0.10)
        self.assertAlmostEqual(events[1]["delta_cost_usd"], 0.27)
        self.assertAlmostEqual(sum(e["delta_cost_usd"] for e in events), 0.37)

    def test_duplicate_snapshot_is_idempotent_no_op(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp))
            for _ in range(3):
                ledger.record_snapshot(
                    repo, provider="grok", model="Grok 4.6", session_id="s1",
                    cumulative_session_cost_usd=0.10, cumulative_session_cost_provenance=EXACT_API,
                    context_used=500, session_input_tokens=400, session_output_tokens=100,
                )
            events = ledger.read_events(repo)

        self.assertEqual(len(events), 1)

    def test_session_reset_treated_as_fresh_delta_not_negative(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp))
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.50, cumulative_session_cost_provenance=EXACT_API,
            )
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.02, cumulative_session_cost_provenance=EXACT_API,
                context_used=10,
            )
            events = ledger.read_events(repo)

        self.assertEqual(len(events), 2)
        self.assertGreaterEqual(events[1]["delta_cost_usd"], 0.0)
        self.assertAlmostEqual(events[1]["delta_cost_usd"], 0.02)

    def test_no_open_mission_is_unattributed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "idle-repo"
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.10, cumulative_session_cost_provenance=EXACT_API,
            )
            events = ledger.read_events(repo)

        self.assertIsNone(events[0]["work_order_id"])
        self.assertEqual(events[0]["attribution"], "unattributed")

    def test_ambiguous_multiple_open_missions_is_unattributed(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp), "M1")
            (repo / ".ooda" / "work-orders" / "M2.json").write_text(json.dumps({"id": "M2"}))
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.10, cumulative_session_cost_provenance=EXACT_API,
            )
            events = ledger.read_events(repo)

        self.assertEqual(events[0]["attribution"], "unattributed")

    def test_completed_mission_no_longer_attributed_after_trace_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp), "M1")
            (repo / ".ooda" / "traces" / "M1.json").write_text(json.dumps({"work_order_id": "M1"}))
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.10, cumulative_session_cost_provenance=EXACT_API,
            )
            events = ledger.read_events(repo)

        self.assertEqual(events[0]["attribution"], "unattributed")

    def test_exact_per_request_usage_takes_priority_over_derived_delta(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp))
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=1.00, cumulative_session_cost_provenance=EXACT_API,
                usage={"cost_in_usd_ticks": 8_300_000, "prompt_tokens": 100, "completion_tokens": 20},
            )
            events = ledger.read_events(repo)

        self.assertAlmostEqual(events[0]["delta_cost_usd"], 0.00083)
        self.assertEqual(events[0]["delta_cost_provenance"], EXACT_API)
        self.assertIn("request_usage", events[0])

    def test_missing_usage_fields_do_not_crash_and_stay_unavailable(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp))
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=None, cumulative_session_cost_provenance=UNAVAILABLE,
            )
            events = ledger.read_events(repo)

        self.assertIsNone(events[0]["delta_cost_usd"])
        self.assertEqual(events[0]["delta_cost_provenance"], UNAVAILABLE)

    def test_cumulative_mission_cost_sums_only_attributed_deltas(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp), "M1")
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.20, cumulative_session_cost_provenance=EXACT_API,
            )
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.55, cumulative_session_cost_provenance=EXACT_API,
            )
            totals = ledger.cumulative_mission_cost(repo)

        self.assertAlmostEqual(totals["M1"], 0.55)

    def test_cost_guzzlers_ranks_by_cost_descending(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo_a = self._repo_with_open_mission(root, "cheap-mission")
            ledger.record_snapshot(
                repo_a, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.05, cumulative_session_cost_provenance=EXACT_API,
            )
            repo_b = root / "other"
            (repo_b / ".ooda" / "work-orders").mkdir(parents=True)
            (repo_b / ".ooda" / "work-orders" / "expensive-mission.json").write_text(
                json.dumps({"id": "expensive-mission"})
            )
            ledger.record_snapshot(
                repo_b, provider="grok", model="Grok 4.6", session_id="s2",
                cumulative_session_cost_usd=0.90, cumulative_session_cost_provenance=EXACT_API,
            )
            rows_a = ledger.cost_guzzlers(repo_a)
            rows_b = ledger.cost_guzzlers(repo_b)

        self.assertEqual(rows_a[0]["label"], "cheap-mission")
        self.assertEqual(rows_b[0]["label"], "expensive-mission")
        self.assertGreater(rows_b[0]["spend_usd"], rows_a[0]["spend_usd"])
        self.assertEqual(rows_a[0]["provenance"], ledger.ATTRIBUTED_SPEND_PROVENANCE)
        self.assertEqual(rows_b[0]["provenance"], ledger.ATTRIBUTED_SPEND_PROVENANCE)

    def test_mission_spend_never_labeled_exact_api_even_from_exact_deltas(self):
        # The per-request delta can be EXACT_API (billed ticks), but the
        # mission attribution wrapping it is always OODA's own inference.
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp), "M1")
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=1.00, cumulative_session_cost_provenance=EXACT_API,
                usage={"cost_in_usd_ticks": 8_300_000, "prompt_tokens": 100, "completion_tokens": 20},
            )
            events = ledger.read_events(repo)
            rows = ledger.cost_guzzlers(repo)

        self.assertEqual(events[0]["delta_cost_provenance"], "EXACT_API")
        self.assertEqual(rows[0]["provenance"], "LOCAL_DERIVED")
        self.assertNotEqual(rows[0]["provenance"], "EXACT_API")

    def test_no_secrets_or_prompts_ever_written_to_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo_with_open_mission(Path(tmp))
            ledger.record_snapshot(
                repo, provider="grok", model="Grok 4.6", session_id="s1",
                cumulative_session_cost_usd=0.10, cumulative_session_cost_provenance=EXACT_API,
                usage={"cost_in_usd_ticks": 100},
            )
            raw_text = ledger.ledger_path(repo).read_text(encoding="utf-8")

        for forbidden in ("api_key", "authorization", "sk-", "xai-", "prompt", "completion_text"):
            self.assertNotIn(forbidden, raw_text.lower())


if __name__ == "__main__":
    unittest.main()
