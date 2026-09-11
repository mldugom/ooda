import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.dashboard import discover_projects, render_html


class DashboardTests(unittest.TestCase):
    def test_discovers_project_in_decision_language_without_promoting_stale_prose(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo"
            (repo / ".ooda/work-orders").mkdir(parents=True)
            (repo / ".ooda/traces").mkdir(parents=True)
            (repo / ".ooda/project.json").write_text(json.dumps({
                "schema": "ooda/project/v1", "project_id": "demo", "project_class": "quantitative-research"
            }))
            (repo / "PROJECT_STATE.md").write_text(
                "# Project State\n\n## Current objective\nSTALE PID 99999 runs an old model.\n\n"
                "## Open decisions / blockers\nSTALE R7 gate.\n\n## Next gate\nSTALE: unfreeze an old stage.\n"
            )
            (repo / ".ooda/project-view.json").write_text(json.dumps({
                "schema": "ooda/project-view/v1",
                "goal": "Make better profitable trade decisions.",
                "decision_served": "Which trades are worth taking?",
                "stakeholder_summary": "STALE PID 99999 from old branch abc1234.",
                "current_question": "Does wallet history beat the market-price benchmark on held-out trades?",
                "evidence": "The benchmark comparison is not yet complete.",
                "uncertainty": "Whether the candidate adds useful held-out signal.",
                "next_step": "Run the frozen benchmark comparison.",
                "timeline": [],
            }))
            (repo / ".ooda/work-orders/DEMO-01.json").write_text(json.dumps({"id": "DEMO-01"}))

            projects = discover_projects(root)
            self.assertEqual(len(projects), 1)
            p = projects[0]
            self.assertEqual(p["project_id"], "demo")
            self.assertEqual(p["status"], "Work in progress")
            self.assertEqual(p["goal"], "Make better profitable trade decisions.")
            self.assertEqual(p["decision"], "Which trades are worth taking?")
            self.assertIn("wallet history", p["current_question"])
            self.assertNotIn("PID 99999", " ".join(str(p.get(k) or "") for k in ("goal", "decision", "current_question", "evidence", "uncertainty", "next_step")))
            self.assertNotIn("unfreeze", p["next_step"])

            page = render_html(projects, 0, root)
            self.assertIn("Prediction Work", page)
            self.assertIn("BUSINESS OBJECTIVE", page)
            self.assertIn("CURRENT MODELING / ENGINEERING QUESTION", page)
            self.assertNotIn("STALE PID 99999", page)
            self.assertNotIn("OBJECTIVE LADDER", page)
            self.assertNotIn("COST GUZZLERS", page)

    def test_open_work_order_can_supply_current_question_but_project_state_cannot(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo"
            (repo / ".ooda/work-orders").mkdir(parents=True)
            (repo / ".ooda/traces").mkdir(parents=True)
            (repo / ".ooda/project.json").write_text(json.dumps({
                "schema": "ooda/project/v1", "project_id": "demo", "project_class": "trading-research"
            }))
            (repo / "PROJECT_STATE.md").write_text(
                "# Project State\n\n## Current objective\nSTALE OLD QUESTION\n"
            )
            (repo / ".ooda/work-orders/current.json").write_text(json.dumps({
                "id": "current", "objective": "Measure whether the candidate improves held-out trade selection."
            }))
            project = discover_projects(root)[0]
            self.assertIn("candidate improves", project["current_question"])
            self.assertNotIn("STALE", project["current_question"])


if __name__ == "__main__":
    unittest.main()
