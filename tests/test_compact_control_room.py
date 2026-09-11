import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.compact_control_room import _current_gate, render_html


class CompactControlRoomTests(unittest.TestCase):
    def test_project_view_human_gate_overrides_stale_project_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ooda = repo / ".ooda"
            ooda.mkdir()
            (ooda / "project-view.json").write_text(json.dumps({
                "schema": "ooda/project-view/v1",
                "human_gate": "Review the fair-value preregistration before any ingest.",
            }))
            project = {"repo": repo, "next_step": "STALE: R7 preregistration"}
            self.assertEqual(_current_gate(project), "Review the fair-value preregistration before any ingest.")

    def test_primary_surface_uses_business_and_data_science_language(self):
        project = {
            "repo": Path("/tmp/demo"),
            "project_id": "crypto-innout",
            "project_class": "trading-research",
            "goal": "Increase risk-adjusted trading profit.",
            "decision": "Which candidate trades should receive capital?",
            "current_question": "Does wallet history beat the market-price benchmark on held-out trades?",
            "evidence": "Candidate improved log loss on the frozen evaluation sample.",
            "uncertainty": "Economic value after fees remains uncertain.",
            "next_step": "Estimate net value after realistic fees and slippage.",
            "status": "Result ready to review",
            "branch": "main", "head": "abc1234", "dirty": "no",
            "work_order": "internal-123", "result_state": "completed", "updated": "now",
            "timeline": [], "session": {},
        }
        page = render_html([project], 0, Path("/tmp"))
        self.assertIn("BUSINESS OBJECTIVE", page)
        self.assertIn("DECISION THIS WORK SHOULD IMPROVE", page)
        self.assertIn("EVIDENCE SO FAR", page)
        self.assertIn("WHAT IS STILL UNCERTAIN", page)
        self.assertIn("NEXT HIGHEST-VALUE STEP", page)
        self.assertIn("Technical details", page)
        self.assertNotIn("OBJECTIVE LADDER", page)
        self.assertNotIn("FEEDBACK-LOOP EFFICIENCY", page)
        self.assertNotIn("COST GUZZLERS", page)
        self.assertNotIn("Role / profile", page)
        self.assertNotIn("Lenses", page)


if __name__ == "__main__":
    unittest.main()
