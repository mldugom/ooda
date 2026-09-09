import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.domain_control_room import render_html


class DomainControlRoomTests(unittest.TestCase):
    def test_compact_domain_cockpit_promotes_value_orientation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "tenniskal"
            ooda = repo / ".ooda"
            ooda.mkdir(parents=True)
            (ooda / "domain-decision-brief.md").write_text(
                """# Domain decision brief\n\n## VALUE FUNCTION\nRepeatable positive after-fee EV on pre-match tennis.\n\n## DECISIONS\nTrade/skip; which side; executable price/time; size.\n\n## CURRENT BOTTLENECK\nNo signed fair-value probability independent of Kalshi.\n""",
                encoding="utf-8",
            )
            (ooda / "project-view.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/project-view/v1",
                        "objective_ladder": [
                            {"status": "completed", "label": "Trustworthy market tape"},
                            {"status": "current", "label": "Preregister PIT sportsbook consensus vs executable Kalshi"},
                            {"status": "provisional", "label": "Test simple signed-edge rule"},
                        ],
                        "timeline": [],
                        "stakeholder_summary": "Consensus is the cheapest first fair-P object; do not fit a tennis model yet.",
                    }
                ),
                encoding="utf-8",
            )
            project = {
                "repo": repo,
                "project_id": "tenniskal",
                "objective": "STALE: R7 preregistration",
                "stage": "review",
                "claim": "n-a",
                "next_gate": "Review fair-value preregistration",
                "stakeholder_summary": "Consensus is the cheapest first fair-P object; do not fit a tennis model yet.",
                "blockers": "Human gate",
                "controller": "needs human gate",
                "branch": "main",
                "head": "abc1234",
                "dirty": "no",
                "updated": "2026-09-09 14:00",
                "work_order": "tk-fair-value-prereg",
                "objective_ladder": [
                    {"status": "completed", "label": "Trustworthy market tape"},
                    {"status": "current", "label": "Preregister PIT sportsbook consensus vs executable Kalshi"},
                    {"status": "provisional", "label": "Test simple signed-edge rule"},
                ],
                "timeline": [],
            }
            page = render_html([project], 0, root)

        self.assertIn("domain-compact-control-room", page)
        self.assertIn("GOAL", page)
        self.assertIn("DECISION", page)
        self.assertIn("BOTTLENECK", page)
        self.assertIn("CURRENT MISSION", page)
        self.assertIn("WHY NOW", page)
        self.assertIn("Repeatable positive after-fee EV on pre-match tennis", page)
        self.assertIn("No signed fair-value probability independent of Kalshi", page)
        self.assertIn("VALUE CRITICAL PATH", page)
        self.assertIn("<details class=\"tech-details\"><summary>Technical state</summary>", page)
        self.assertIn("<p>STALE: R7 preregistration</p>", page)
        self.assertNotIn("VALUE CRITICAL PATH / CURRENT ORIENTATION", page)


if __name__ == "__main__":
    unittest.main()
