import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.dashboard import discover_projects, render_html


class DashboardTests(unittest.TestCase):
    def test_discovers_project_in_decision_language(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo"
            (repo / ".ooda/work-orders").mkdir(parents=True)
            (repo / ".ooda/traces").mkdir(parents=True)
            (repo / ".ooda/project.json").write_text(json.dumps({
                "schema": "ooda/project/v1", "project_id": "demo", "project_class": "quantitative-research"
            }))
            (repo / "PROJECT_STATE.md").write_text(
                "# Project State\n\n## Current objective\nTest whether wallet history improves prediction quality.\n\n"
                "## Open decisions / blockers\nNeed more held-out evidence.\n\n## Next gate\nCompare against the current benchmark.\n"
            )
            (repo / ".ooda/project-view.json").write_text(json.dumps({
                "schema": "ooda/project-view/v1",
                "goal": "Make better profitable trade decisions.",
                "decision_served": "Which trades are worth taking?",
                "stakeholder_summary": "Early evidence is promising but not decisive.",
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

            page = render_html(projects, 0, root)
            self.assertIn("Prediction Work", page)
            self.assertIn("BUSINESS OBJECTIVE", page)
            self.assertIn("CURRENT MODELING / ENGINEERING QUESTION", page)
            self.assertNotIn("OBJECTIVE LADDER", page)
            self.assertNotIn("COST GUZZLERS", page)


if __name__ == "__main__":
    unittest.main()
