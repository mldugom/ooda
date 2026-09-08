import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.grok_statusline import configure_status_line, render


class GrokStatusLineTests(unittest.TestCase):
    def test_renders_project_current_gate_and_worker(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td) / "tenniskal"
            (repo / ".ooda" / "work-orders").mkdir(parents=True)
            (repo / ".ooda" / "traces").mkdir(parents=True)
            (repo / ".ooda" / "project.json").write_text(
                json.dumps({"schema": "ooda/project/v1", "project_id": "tenniskal"}),
                encoding="utf-8",
            )
            (repo / ".ooda" / "project-view.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/project-view/v1",
                        "project_id": "tenniskal",
                        "objective_ladder": [
                            {"status": "current", "label": "Design the R7 preregistration"}
                        ],
                        "timeline": [
                            {
                                "at": "2026-09-08",
                                "decision": "R6 integrated",
                                "so_what": "R7 can now be designed.",
                                "bigger_idea": "Move from exploration to controlled testing.",
                            }
                        ],
                        "stakeholder_summary": "R6 is complete.",
                    }
                ),
                encoding="utf-8",
            )
            (repo / "PROJECT_STATE.md").write_text(
                "# Project State\n\n## Next gate\nApprove the R7 preregistration mission.\n",
                encoding="utf-8",
            )

            payload = {
                "workspace": {"current_dir": str(repo), "branch": "main"},
                "model": {"display_name": "Grok 4.6"},
                "context_window": {"used_percentage": 12.2},
            }
            text = render(payload, columns=160)

        self.assertIn("tenniskal │ Grok 4.6 │ 12% ctx │ main", text)
        self.assertIn("OODA ● Design the R7 preregistration", text)
        self.assertIn("GATE → Approve the R7 preregistration mission.", text)
        self.assertIn("worker: idle", text)
        self.assertIn("LAST PIVOT → R6 integrated", text)

    def test_configure_replaces_only_status_line_section(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "config.toml"
            path.write_text(
                "[models]\ndefault = \"grok-build\"\n\n"
                "[ui.status_line]\ntype = \"builtin\"\nitems = [\"cwd\"]\n\n"
                "[workflows]\nenabled = true\n",
                encoding="utf-8",
            )
            changed = configure_status_line(
                path,
                command="/tmp/ooda statusline",
                refresh_seconds=600,
                backup=False,
            )
            text = path.read_text(encoding="utf-8")

        self.assertTrue(changed)
        self.assertIn('[models]\ndefault = "grok-build"', text)
        self.assertIn('[workflows]\nenabled = true', text)
        self.assertIn('[ui.status_line]\ntype = "command"', text)
        self.assertIn('command = "/tmp/ooda statusline"', text)
        self.assertIn("refresh_interval = 600", text)
        self.assertNotIn('items = ["cwd"]', text)


if __name__ == "__main__":
    unittest.main()
