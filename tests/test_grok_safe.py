import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import grok_safe


class GrokSafeTests(unittest.TestCase):
    def _command(self, env=None):
        captured = {}

        def fake_call(command):
            captured["command"] = command
            return 0

        clean_keys = {"OODA_GROK_NO_SUBAGENTS": "", "OODA_GROK_MAX_TURNS": ""}
        clean_keys.update(env or {})
        with patch.object(grok_safe, "_grok_binary", return_value="/usr/bin/grok"):
            with patch.object(grok_safe, "_configure_ooda_status_line"):
                with patch.object(grok_safe, "_warn_if_workflows_disabled"):
                    with patch.object(grok_safe.subprocess, "call", side_effect=fake_call):
                        with patch.object(sys, "argv", ["grok-safe"]):
                            with patch.dict(os.environ, clean_keys, clear=False):
                                for key, value in list(clean_keys.items()):
                                    if value == "":
                                        os.environ.pop(key, None)
                                with self.assertRaises(SystemExit) as ctx:
                                    grok_safe.main()
        self.assertEqual(ctx.exception.code, 0)
        return captured["command"]

    def test_controller_friendly_defaults(self):
        command = self._command()
        self.assertNotIn("--no-subagents", command)
        self.assertNotIn("--max-turns", command)
        self.assertIn("--rules", command)

    def test_strict_mode_can_disable_subagents(self):
        command = self._command({"OODA_GROK_NO_SUBAGENTS": "1"})
        self.assertIn("--no-subagents", command)

    def test_optional_hard_turn_cap(self):
        command = self._command({"OODA_GROK_MAX_TURNS": "12"})
        idx = command.index("--max-turns")
        self.assertEqual(command[idx + 1], "12")

    def test_workflows_disabled_detection(self):
        text = """
[models]
default = "grok-4.6"

[workflows]
enabled = false

[privacy]
privacy_banner_acked = "x"
"""
        self.assertTrue(grok_safe._workflows_explicitly_disabled(text))
        self.assertFalse(grok_safe._workflows_explicitly_disabled(text.replace("false", "true")))

    def test_workflows_disabled_ignores_other_enabled_keys(self):
        text = """
[other]
enabled = false
[workflows]
# enabled = false
"""
        self.assertFalse(grok_safe._workflows_explicitly_disabled(text))

    def test_status_line_can_be_disabled_by_env(self):
        with patch.dict(os.environ, {"OODA_GROK_STATUSLINE": "0"}, clear=False):
            with patch.object(grok_safe, "_ooda_cli") as ooda_cli:
                grok_safe._configure_ooda_status_line()
        ooda_cli.assert_not_called()


if __name__ == "__main__":
    unittest.main()
