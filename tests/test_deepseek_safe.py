import io
import sys
import unittest
from unittest import mock

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "src"))
from ooda import deepseek_safe


class DeepSeekSafeTests(unittest.TestCase):
    def test_parked_launcher_fails_closed(self):
        stderr = io.StringIO()
        with mock.patch.object(sys, "stderr", stderr):
            with self.assertRaises(SystemExit) as ctx:
                deepseek_safe.main()
        self.assertEqual(ctx.exception.code, 2)
        text = stderr.getvalue()
        self.assertIn("parked", text.lower())
        self.assertIn("grok-safe", text)


if __name__ == "__main__":
    unittest.main()
