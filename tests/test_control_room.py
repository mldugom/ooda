import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.control_room import _session_context, render_html


class ControlRoomTests(unittest.TestCase):
    def _project(self, repo: Path):
        return {
            "repo": repo,
            "project_id": "tenniskal",
            "objective": "Preregister R7 without outcome access",
            "stage": "review",
            "claim": "evidence",
            "next_gate": "Integration Owner approves R7 preregistration",
            "stakeholder_summary": "R6 is frozen; R7 compute is not authorized.",
            "blockers": "Human gate only",
            "role": "architect",
            "profile": "quantitative-research",
            "work_order": "tk-r7-prereg",
            "result_state": "needs_human_gate",
            "controller": "needs human gate",
            "branch": "main",
            "head": "7c220a7",
            "dirty": "no",
            "updated": "2026-09-08 01:30",
            "objective_ladder": [
                {"status": "completed", "label": "Freeze ALPHA_HYPOTHESES_V1"},
                {"status": "current", "label": "Preregister R7"},
                {"status": "provisional", "label": "Run R7 under frozen protocol"},
            ],
            "timeline": [
                {
                    "at": "2026-09-08",
                    "decision": "Freeze V1",
                    "so_what": "Open-ended EDA stops",
                    "bigger_idea": "Outcome tests cannot redesign features",
                }
            ],
        }

    def test_renders_live_control_room_without_cost_ui(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            (repo / ".ooda").mkdir(parents=True)
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertIn("OODA Control Room", page)
        self.assertIn("LIVE OODA LOOP", page)
        self.assertIn("OBJECTIVE LADDER", page)
        self.assertIn("MATERIAL DECISION TIMELINE", page)
        self.assertIn("Preregister R7", page)
        self.assertIn("CURRENT", page)
        self.assertIn("SESSION CONTEXT", page)
        self.assertIn("provider UI", page)
        self.assertNotIn("SESSION COST", page)
        self.assertNotIn("$", page)

    def test_optional_context_telemetry_renders_percent(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            (repo / ".ooda").mkdir(parents=True)
            (repo / ".ooda/session-telemetry.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/session-telemetry/v1",
                        "provider": "grok",
                        "context_used": 29000,
                        "context_limit": 500000,
                        "updated_at": "2026-09-08T01:30:00-04:00",
                    }
                )
            )
            telemetry = _session_context(repo)
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertIsNotNone(telemetry)
        self.assertAlmostEqual(telemetry["pct"], 5.8)
        self.assertIn("5.8%", page)
        self.assertIn("29K / 500K", page)


if __name__ == "__main__":
    unittest.main()
