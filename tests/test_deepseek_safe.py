import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src"))
from ooda import deepseek_safe


class DeepSeekSafeTests(unittest.TestCase):
    def _run(self, env=None):
        captured = {}

        def fake_call(command, env=None):
            captured["command"] = command
            captured["env"] = dict(env or {})
            return 0

        with mock.patch.object(deepseek_safe, "_deepseek_binary", return_value="/usr/bin/deepseek"), mock.patch.object(
            deepseek_safe, "_skills_ready", return_value=True
        ), mock.patch.object(deepseek_safe.subprocess, "call", side_effect=fake_call), mock.patch.object(
            sys, "argv", ["deepseek-safe"]
        ), mock.patch.dict(os.environ, env or {}, clear=False):
            if not env or "DEEPSEEK_MODEL" not in env:
                os.environ.pop("DEEPSEEK_MODEL", None)
            with self.assertRaises(SystemExit) as ctx:
                deepseek_safe.main()
        self.assertEqual(ctx.exception.code, 0)
        return captured

    def test_defaults_controller_to_v4_pro(self):
        captured = self._run()
        self.assertEqual(captured["command"], ["/usr/bin/deepseek"])
        self.assertEqual(captured["env"]["DEEPSEEK_MODEL"], "deepseek-v4-pro")

    def test_preserves_explicit_model(self):
        captured = self._run({"DEEPSEEK_MODEL": "deepseek-v4-flash"})
        self.assertEqual(captured["env"]["DEEPSEEK_MODEL"], "deepseek-v4-flash")

    def test_requires_installed_ooda_skills(self):
        with mock.patch.object(deepseek_safe, "_deepseek_binary", return_value="/usr/bin/deepseek"), mock.patch.object(
            deepseek_safe, "_skills_ready", return_value=False
        ), mock.patch.object(sys, "argv", ["deepseek-safe"]):
            with self.assertRaises(SystemExit) as ctx:
                deepseek_safe.main()
        self.assertEqual(ctx.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
