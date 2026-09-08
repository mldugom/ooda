import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import dashboard, project_view


SAMPLE = {
    "schema": "ooda/project-view/v1",
    "project_id": "sample",
    "objective_ladder": [
        {"status": "completed", "label": "Understand the substrate"},
        {"status": "current", "label": "Test the frozen hypotheses"},
        {"status": "provisional", "label": "Evaluate live execution"},
    ],
    "timeline": [
        {
            "at": "Sep 7",
            "decision": "Freeze the candidate set",
            "so_what": "The next experiment cannot add features after seeing results.",
            "bigger_idea": "The program is moving from exploration into controlled testing.",
        }
    ],
    "stakeholder_summary": "The project has frozen its candidate hypotheses and is ready to design the next controlled test.",
}


class ProjectViewTests(unittest.TestCase):
    def test_valid_project_view(self):
        self.assertEqual(project_view.validate_project_view(SAMPLE), [])

    def test_requires_exactly_one_current_rung(self):
        data = json.loads(json.dumps(SAMPLE))
        data["objective_ladder"][1]["status"] = "provisional"
        errors = project_view.validate_project_view(data)
        self.assertIn("objective_ladder must contain exactly one current rung", errors)

    def test_terminal_renderer_has_ladder_timeline_and_summary(self):
        rendered = project_view.render_text(SAMPLE)
        self.assertIn("OBJECTIVE LADDER — sample", rendered)
        self.assertIn("● CURRENT Test the frozen hypotheses", rendered)
        self.assertIn("DECISION", rendered)
        self.assertIn("IMMEDIATE CONSEQUENCE", rendered)
        self.assertIn("PROGRAM IMPACT", rendered)
        self.assertNotIn("SO WHAT", rendered)
        self.assertNotIn("BIGGER IDEA", rendered)
        self.assertIn("CURRENT STAKEHOLDER SUMMARY", rendered)

    def test_cli_reads_project_view(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            path = repo / ".ooda" / "project-view.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(SAMPLE), encoding="utf-8")
            out = StringIO()
            with redirect_stdout(out):
                rc = project_view.main([str(repo)])
            self.assertEqual(rc, 0)
            self.assertIn("Freeze the candidate set", out.getvalue())

    def test_cli_missing_view_is_clear(self):
        with tempfile.TemporaryDirectory() as td:
            err = StringIO()
            with redirect_stderr(err):
                rc = project_view.main([td])
            self.assertEqual(rc, 2)
            self.assertIn("No durable project view", err.getvalue())

    def test_dashboard_renders_project_view(self):
        project = {
            "project_id": "sample",
            "project_class": "quantitative-research",
            "objective": "Test frozen hypotheses",
            "stage": "orient",
            "controller": "idle",
            "work_order": "—",
            "role": "—",
            "profile": "—",
            "lenses": [],
            "claim": "n-a",
            "result_state": "—",
            "result_summary": "—",
            "blockers": "None",
            "next_gate": "Design the next test",
            "branch": "main",
            "head": "abc1234",
            "dirty": "no",
            "updated": "2026-09-08 00:00",
            "objective_ladder": SAMPLE["objective_ladder"],
            "timeline": SAMPLE["timeline"],
            "stakeholder_summary": SAMPLE["stakeholder_summary"],
        }
        html = dashboard.render_html([project], 0, Path("/tmp"))
        self.assertIn("CURRENT STAKEHOLDER SUMMARY", html)
        self.assertIn("OBJECTIVE LADDER", html)
        self.assertIn("RECENT DECISION TIMELINE", html)
        self.assertIn("Freeze the candidate set", html)


if __name__ == "__main__":
    unittest.main()
