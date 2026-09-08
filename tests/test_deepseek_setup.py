import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.deepseek_setup import configure_hook


class DeepSeekSetupTests(unittest.TestCase):
    def test_hook_configuration_preserves_unrelated_sections(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text(
                '[model]\ndefault = "deepseek-v4-pro"\n\n'
                '[sandbox]\nmode = "seatbelt"\n',
                encoding="utf-8",
            )
            changed, warning = configure_hook(path, "/tmp/ooda deepseek-telemetry")
            text = path.read_text(encoding="utf-8")

        self.assertTrue(changed)
        self.assertIsNone(warning)
        self.assertIn('[model]\ndefault = "deepseek-v4-pro"', text)
        self.assertIn('[sandbox]\nmode = "seatbelt"', text)
        self.assertIn('[hooks]\nenabled = true', text)
        self.assertIn('name = "ooda-telemetry"', text)
        self.assertIn('event = "turn_end"', text)
        self.assertIn('command = "/tmp/ooda deepseek-telemetry"', text)

    def test_replaces_only_existing_ooda_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text(
                '[hooks]\nenabled = true\n\n'
                '[[hooks.hooks]]\nname = "other-hook"\nevent = "turn_end"\ncommand = "/tmp/other"\n\n'
                '[[hooks.hooks]]\nname = "ooda-telemetry"\nevent = "turn_end"\ncommand = "/old/ooda"\n',
                encoding="utf-8",
            )
            changed, warning = configure_hook(path, "/new/ooda deepseek-telemetry")
            text = path.read_text(encoding="utf-8")

        self.assertTrue(changed)
        self.assertIsNone(warning)
        self.assertEqual(text.count('name = "ooda-telemetry"'), 1)
        self.assertIn('name = "other-hook"', text)
        self.assertIn('command = "/tmp/other"', text)
        self.assertIn('command = "/new/ooda deepseek-telemetry"', text)
        self.assertNotIn('/old/ooda', text)

    def test_preserves_explicit_hooks_disabled_and_warns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "config.toml"
            path.write_text('[hooks]\nenabled = false\n', encoding="utf-8")
            changed, warning = configure_hook(path, "/tmp/ooda deepseek-telemetry")
            text = path.read_text(encoding="utf-8")

        self.assertTrue(changed)
        self.assertIsNotNone(warning)
        self.assertIn('[hooks]\nenabled = false', text)
        self.assertNotIn('[hooks]\nenabled = true', text)
        self.assertIn('name = "ooda-telemetry"', text)


if __name__ == "__main__":
    unittest.main()
