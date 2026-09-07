import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import grok_safe


class GrokSafeTests(unittest.TestCase):
    def test_subagents_allowed_by_default(self):
        captured = {}

        def fake_call(command):
            captured["command"] = command
            return 0

        with patch.object(grok_safe, "_grok_binary", return_value="/usr/bin/grok"):
            with patch.object(grok_safe.subprocess, "call", side_effect=fake_call):
                with patch.object(sys, "argv", ["grok-safe"]):
                    with patch.dict(os.environ, {}, clear=False):
                        os.environ.pop("OODA_GROK_NO_SUBAGENTS", None)
                        with self.assertRaises(SystemExit) as ctx:
                            grok_safe.main()
        self.assertEqual(ctx.exception.code, 0)
        self.assertNotIn("--no-subagents", captured["command"])
        self.assertIn("--max-turns", captured["command"])

    def test_strict_mode_can_disable_subagents(self):
        captured = {}

        def fake_call(command):
            captured["command"] = command
            return 0

        with patch.object(grok_safe, "_grok_binary", return_value="/usr/bin/grok"):
            with patch.object(grok_safe.subprocess, "call", side_effect=fake_call):
                with patch.object(sys, "argv", ["grok-safe"]):
                    with patch.dict(os.environ, {"OODA_GROK_NO_SUBAGENTS": "1"}, clear=False):
                        with self.assertRaises(SystemExit):
                            grok_safe.main()
        self.assertIn("--no-subagents", captured["command"])


if __name__ == "__main__":
    unittest.main()
