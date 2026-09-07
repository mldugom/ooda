import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.dashboard import discover_projects, render_html


class DashboardTests(unittest.TestCase):
    def test_discovers_adopted_repo_and_renders_control_room(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "demo"
            (repo / ".ooda/work-orders").mkdir(parents=True)
            (repo / ".ooda/traces").mkdir(parents=True)
            (repo / ".ooda/project.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/project/v1",
                        "project_id": "demo",
                        "project_class": "software-product",
                    }
                )
            )
            (repo / "PROJECT_STATE.md").write_text(
                "# Project State\n\n"
                "## Current objective\nShip one vertical slice.\n\n"
                "## Open decisions / blockers\n- None\n\n"
                "## Next gate\nReview UX\n"
            )
            (repo / ".ooda/work-orders/DEMO-01.json").write_text(
                json.dumps(
                    {
                        "id": "DEMO-01",
                        "role": "engineer",
                        "profile": "full-stack",
                        "claim_level": "n-a",
                        "lenses": ["product-user"],
                    }
                )
            )

            projects = discover_projects(root)
            self.assertEqual(len(projects), 1)
            self.assertEqual(projects[0]["project_id"], "demo")
            self.assertEqual(projects[0]["stage"], "act")
            self.assertEqual(projects[0]["work_order"], "DEMO-01")

            page = render_html(projects, 60, root)
            self.assertIn("OODA Control Room", page)
            self.assertIn("Refresh now", page)
            self.assertIn("Ship one vertical slice", page)


if __name__ == "__main__":
    unittest.main()
