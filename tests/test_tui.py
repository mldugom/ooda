import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ooda.tui import render_screen, route_input


class TuiTests(unittest.TestCase):
    def _project(self, repo: Path):
        return {
            "repo": repo,
            "project_id": "tenniskal",
            "objective": "Design the R7 preregistration",
            "stage": "review",
            "controller": "needs human gate",
            "work_order": "tk-r7-prereg",
            "role": "architect",
            "blockers": "Human gate only",
            "next_gate": "Lawrence approves the frozen R7 preregistration",
            "objective_ladder": [
                {"status": "completed", "label": "R6 market-state exploration"},
                {"status": "current", "label": "Controlled predictive test"},
                {"status": "provisional", "label": "Player win probability"},
            ],
            "timeline": [
                {
                    "at": "2026-09-08",
                    "decision": "Freeze ALPHA_HYPOTHESES_V1 before outcome access",
                    "so_what": "R7 cannot redesign the feature set after outcomes are visible",
                    "bigger_idea": "Move from exploration to controlled testing",
                }
            ],
        }

    def test_renders_compact_ooda_cockpit(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            (repo / ".ooda").mkdir(parents=True)
            screen = render_screen([self._project(repo)], repo, model="deepseek-v4-pro", balance=3.8, width=120)

        self.assertIn("PROJECTS", screen)
        self.assertIn("TENNISKAL", screen)
        self.assertIn("CURRENT", screen)
        self.assertIn("WAITING ON", screen)
        self.assertIn("DECIDE", screen)
        self.assertIn("OBJECTIVE", screen)
        self.assertIn("LAST MATERIAL DECISION", screen)
        self.assertIn("ALPHA_HYPOTHESES_V1", screen)
        self.assertIn("balance $3.80", screen)
        self.assertIn("/ooda-controller", screen)

    def test_ooda_controller_command_expands_to_skill_prompt(self):
        action, payload = route_input("/ooda-controller where are we?")
        self.assertEqual(action, "prompt")
        self.assertIn("Use the ooda-controller skill", payload)
        self.assertIn("where are we?", payload)

    def test_typo_alias_is_supported(self):
        action, payload = route_input("/ooda-contorller timeline")
        self.assertEqual(action, "prompt")
        self.assertIn("ooda-controller skill", payload)
        self.assertIn("timeline", payload)

    def test_ooda_worker_command_expands_to_skill_prompt(self):
        action, payload = route_input("/ooda .ooda/work-orders/test.json")
        self.assertEqual(action, "prompt")
        self.assertIn("Use the ooda skill", payload)
        self.assertIn(".ooda/work-orders/test.json", payload)

    def test_unknown_provider_slash_command_fails_clearly(self):
        action, payload = route_input("/plugin")
        self.assertEqual(action, "error")
        self.assertIn("Provider-native slash menus", payload)


if __name__ == "__main__":
    unittest.main()
