import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.compact_control_room import _current_gate


class CompactControlRoomTests(unittest.TestCase):
    def test_project_view_human_gate_overrides_stale_project_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            ooda = repo / ".ooda"
            ooda.mkdir()
            (ooda / "project-view.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/project-view/v1",
                        "human_gate": "Review the fair-value preregistration before any ingest.",
                    }
                ),
                encoding="utf-8",
            )
            project = {
                "repo": repo,
                "next_gate": "STALE: R7 preregistration",
            }
            self.assertEqual(
                _current_gate(project),
                "Review the fair-value preregistration before any ingest.",
            )


if __name__ == "__main__":
    unittest.main()
