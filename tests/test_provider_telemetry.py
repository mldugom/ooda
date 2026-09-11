import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import provider_telemetry


class ProviderTelemetryTests(unittest.TestCase):
    def _repo(self, root: Path, name="demo") -> Path:
        repo = root / name
        (repo / ".ooda").mkdir(parents=True)
        (repo / ".ooda/project.json").write_text(json.dumps({"schema": "ooda/project/v1", "project_id": name}))
        return repo

    def test_grok_payload_persists_only_useful_session_facts(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp), "tenniskal")
            payload = {
                "workspace": {"current_dir": str(repo)},
                "model": {"display_name": "Grok 4.6", "id": "grok-4.6"},
                "context_window": {"context_tokens": 29000, "context_window_size": 500000, "used_percentage": 5.8},
                "cost": {"total_cost_usd": 0.37},
                "effort": {"level": "medium"},
                "session_id": "abc",
                "usage": {"prompt_tokens": 1000},
                "api_key": "secret",
            }
            target = provider_telemetry.record_grok_payload(payload)
            data = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(data["provider"], "grok")
        self.assertEqual(data["model"], "Grok 4.6")
        self.assertEqual(data["session_id"], "abc")
        self.assertEqual(data["context_used"], 29000)
        self.assertEqual(data["session_cost_usd"], 0.37)
        self.assertEqual(data["session_cost_provenance"], "PROVIDER_REPORTED")
        self.assertEqual(data["effort_provenance"], "PROVIDER_REPORTED")
        self.assertNotIn("last_request_usage", data)
        self.assertNotIn("current_mission_id", data)

    def test_payload_does_not_create_a_cost_ledger(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            provider_telemetry.record_grok_payload({
                "workspace": {"current_dir": str(repo)},
                "session_id": "s1",
                "cost": {"total_cost_usd": 0.2},
            })
            self.assertFalse((repo / ".ooda" / "telemetry-ledger.jsonl").exists())

    def test_secrets_and_arbitrary_usage_are_not_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            target = provider_telemetry.record_grok_payload({
                "workspace": {"current_dir": str(repo)},
                "api_key": "xai-secret",
                "usage": {"prompt": "private", "prompt_tokens": 99},
            })
            raw = target.read_text(encoding="utf-8")
        self.assertNotIn("xai-secret", raw)
        self.assertNotIn("private", raw)
        self.assertNotIn("prompt_tokens", raw)

    def test_worker_effort_is_never_inferred_from_parent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            target = provider_telemetry.record_grok_payload({
                "workspace": {"current_dir": str(repo)},
                "effort": {"level": "high"},
            })
            data = json.loads(target.read_text(encoding="utf-8"))
        self.assertEqual(data["effort"], "high")
        self.assertIsNone(data["worker_effort"])
        self.assertEqual(data["worker_effort_provenance"], "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
