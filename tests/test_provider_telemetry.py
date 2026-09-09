import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import provider_telemetry


class ProviderTelemetryTests(unittest.TestCase):
    def _repo(self, root: Path, name="demo") -> Path:
        repo = root / name
        (repo / ".ooda").mkdir(parents=True)
        (repo / ".ooda/project.json").write_text(
            json.dumps({"schema": "ooda/project/v1", "project_id": name}),
            encoding="utf-8",
        )
        return repo

    def test_grok_payload_persists_model_context_and_metered_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            payload = {
                "workspace": {"current_dir": str(repo), "branch": "main"},
                "model": {"display_name": "Grok 4.6", "id": "grok-4.6"},
                "context_window": {
                    "context_tokens": 29000,
                    "context_window_size": 500000,
                    "used_percentage": 5.8,
                    "session_input_tokens": 25000,
                    "session_output_tokens": 4000,
                },
                "cost": {"total_cost_usd": 0.37},
                "effort": {"level": "medium"},
                "session_id": "abc",
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(data["provider"], "grok")
        self.assertEqual(data["model"], "Grok 4.6")
        self.assertEqual(data["context_used"], 29000)
        self.assertEqual(data["context_limit"], 500000)
        self.assertEqual(data["session_cost_usd"], 0.37)
        self.assertEqual(data["session_cost_kind"], "provider-metered")

    def test_grok_payload_never_persists_secrets(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6"},
                "api_key": "xai-should-never-be-here",
                "cost": {"total_cost_usd": 0.1},
            }
            target = provider_telemetry.record_grok_payload(payload)
            raw = target.read_text(encoding="utf-8")

        self.assertNotIn("xai-should-never-be-here", raw)

    def test_grok_payload_with_exact_usage_populates_ledger_and_last_request(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            (repo / ".ooda" / "traces").mkdir(parents=True)
            (repo / ".ooda" / "work-orders" / "M1.json").write_text(json.dumps({"id": "M1"}))
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6"},
                "session_id": "sess-1",
                "cost": {"total_cost_usd": 0.00083},
                "usage": {
                    "cost_in_usd_ticks": 8_300_000,
                    "prompt_tokens": 1000,
                    "prompt_tokens_details": {"cached_tokens": 400},
                    "completion_tokens": 200,
                },
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))
            from ooda.telemetry_ledger import read_events

            events = read_events(repo)

        self.assertIn("last_request_usage", data)
        self.assertAlmostEqual(data["last_request_usage"]["cost_usd"], 0.00083)
        self.assertEqual(data["current_mission_id"], "M1")
        self.assertAlmostEqual(data["current_mission_attributed_spend_usd"], 0.00083)
        self.assertEqual(data["current_mission_attributed_spend_provenance"], "LOCAL_DERIVED")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["attribution"], "mission")

    def test_mission_attributed_spend_never_marked_exact_api(self):
        # Even though the underlying per-request usage was itself exact
        # (billed ticks), attribution to a named mission is always OODA's
        # own inference — it must never be labeled EXACT_API.
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            (repo / ".ooda" / "traces").mkdir(parents=True)
            (repo / ".ooda" / "work-orders" / "M1.json").write_text(json.dumps({"id": "M1"}))
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6"},
                "session_id": "sess-1",
                "cost": {"total_cost_usd": 0.00083},
                "usage": {"cost_in_usd_ticks": 8_300_000, "prompt_tokens": 100, "completion_tokens": 20},
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(data["current_mission_attributed_spend_provenance"], "LOCAL_DERIVED")
        self.assertNotEqual(data["current_mission_attributed_spend_provenance"], "EXACT_API")

    def test_grok_payload_without_usage_leaves_last_request_and_mission_cost_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6"},
                "cost": {"total_cost_usd": 0.1},
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertNotIn("last_request_usage", data)
        self.assertNotIn("current_mission_id", data)
        self.assertNotIn("current_mission_attributed_spend_usd", data)

    def test_effort_present_recorded_with_provenance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6"},
                "effort": {"level": "xhigh"},
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(data["effort"], "xhigh")
        self.assertEqual(data["effort_provenance"], "EXACT_API")

    def test_effort_absent_is_unavailable_not_fabricated(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6"},
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(data["effort"], "")
        self.assertEqual(data["effort_provenance"], "UNAVAILABLE")

    def test_worker_effort_always_unavailable_never_inherits_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6"},
                "effort": {"level": "high"},
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(data["effort"], "high")
        self.assertIsNone(data["worker_effort"])
        self.assertEqual(data["worker_effort_provenance"], "UNAVAILABLE")
        self.assertNotEqual(data["worker_effort"], data["effort"])

    def test_deepseek_turn_persists_context_estimate_and_balance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "crypto-innout")
            payload = {
                "workspace": str(repo),
                "provider": "deepseek",
                "model": "deepseek-v4-pro",
                "session_id": "ds1",
                "totals": {
                    "conversation_tokens": 84000,
                    "session_tokens": 92000,
                    "input_tokens": 78000,
                    "output_tokens": 14000,
                },
            }
            env = {
                "DEEPSEEK_WORKSPACE": str(repo),
                "DEEPSEEK_API_KEY": "test-key",
                "DEEPSEEK_SESSION_COST": "0.07",
            }
            with mock.patch.object(
                provider_telemetry,
                "_fetch_deepseek_balance",
                return_value={
                    "account_balance": 9.62,
                    "account_topped_up_balance": 9.00,
                    "account_granted_balance": 0.62,
                    "currency": "USD",
                },
            ):
                target = provider_telemetry.record_deepseek_turn(payload, env)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(data["provider"], "deepseek")
        self.assertEqual(data["model"], "deepseek-v4-pro")
        self.assertEqual(data["context_used"], 84000)
        self.assertEqual(data["context_limit"], 1000000)
        self.assertAlmostEqual(data["context_percent"], 8.4)
        self.assertEqual(data["session_cost_usd"], 0.07)
        self.assertEqual(data["session_cost_kind"], "tui-estimate")
        self.assertEqual(data["account_balance"], 9.62)
        self.assertEqual(data["account_currency"], "USD")

    def test_deepseek_balance_cache_avoids_repeat_lookup(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            (repo / ".ooda/session-telemetry.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/session-telemetry/v1",
                        "provider": "deepseek",
                        "account_balance": 8.50,
                        "account_currency": "USD",
                        "balance_checked_unix": 1000.0,
                    }
                ),
                encoding="utf-8",
            )
            payload = {"workspace": str(repo), "totals": {"conversation_tokens": 1000}}
            env = {"DEEPSEEK_API_KEY": "test-key"}
            with mock.patch.object(provider_telemetry.time, "time", return_value=1100.0), mock.patch.object(
                provider_telemetry, "_fetch_deepseek_balance"
            ) as fetch:
                target = provider_telemetry.record_deepseek_turn(payload, env)
            data = json.loads(target.read_text(encoding="utf-8"))

        fetch.assert_not_called()
        self.assertEqual(data["account_balance"], 8.50)


if __name__ == "__main__":
    unittest.main()
