import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.compact_control_room import _current_gate, render_html


class CompactControlRoomTests(unittest.TestCase):
    def test_current_gate_uses_only_collected_trusted_next_step(self):
        project = {
            "repo": Path("/tmp/demo"),
            "next_step": "Compare the candidate with the current benchmark on held-out data.",
        }
        self.assertEqual(
            _current_gate(project),
            "Compare the candidate with the current benchmark on held-out data.",
        )

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

    def test_dashboard_says_when_current_decision_state_needs_refresh(self):
        project = {
            "repo": Path("/tmp/demo"),
            "project_id": "crypto-innout",
            "project_class": "trading-research",
            "goal": "Increase profitable prediction quality.",
            "decision": "Which opportunities deserve capital?",
            "current_question": "",
            "evidence": "",
            "uncertainty": "",
            "next_step": "",
            "status": "Ready to choose next work",
            "branch": "main", "head": "abc1234", "dirty": "no",
            "work_order": "", "result_state": "", "updated": "now",
            "timeline": [], "session": {},
        }
        page = render_html([project], 0, Path("/tmp"))
        self.assertIn("Current decision state needs a refresh", page)
        self.assertIn("ooda run", page)


if __name__ == "__main__":
    unittest.main()
