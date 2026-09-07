import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts" / "install-cli.sh"


class InstallCliTests(unittest.TestCase):
    def test_legacy_grok_safe_symlink_is_upgraded(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            bin_dir = home / ".local" / "bin"
            home.mkdir(parents=True)
            bin_dir.mkdir(parents=True)

            legacy = bin_dir / "grok-safe"
            legacy.symlink_to(ROOT / "scripts" / "grok-safe")

            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "OODA_BIN_DIR": str(bin_dir),
                    "SHELL": "/bin/bash",
                    "PATH": f"{bin_dir}:{env.get('PATH', '')}",
                }
            )
            cp = subprocess.run(
                ["bash", str(INSTALLER)],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(cp.returncode, 0, cp.stderr)
            self.assertFalse(legacy.is_symlink())
            text = legacy.read_text(encoding="utf-8")
            self.assertIn(f"# OODA source: {ROOT}", text)
            self.assertIn("python3 -m ooda.grok_safe", text)
            self.assertIn("Upgraded legacy OODA", cp.stdout)

    def test_unknown_grok_safe_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            bin_dir = home / ".local" / "bin"
            home.mkdir(parents=True)
            bin_dir.mkdir(parents=True)

            unknown = bin_dir / "grok-safe"
            unknown.write_text("#!/bin/sh\necho unrelated\n", encoding="utf-8")

            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "OODA_BIN_DIR": str(bin_dir),
                    "SHELL": "/bin/bash",
                    "PATH": f"{bin_dir}:{env.get('PATH', '')}",
                }
            )
            cp = subprocess.run(
                ["bash", str(INSTALLER)],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(cp.returncode, 2)
            self.assertEqual(unknown.read_text(encoding="utf-8"), "#!/bin/sh\necho unrelated\n")
            self.assertIn("Refusing to replace existing", cp.stderr)

    def test_macos_bash_persists_path_in_bash_profile(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            bin_dir = home / ".local" / "bin"
            home.mkdir(parents=True)

            env = os.environ.copy()
            env.update(
                {
                    "HOME": str(home),
                    "OODA_BIN_DIR": str(bin_dir),
                    "SHELL": "/bin/bash",
                    "OODA_OS_NAME": "Darwin",
                    "PATH": env.get("PATH", ""),
                }
            )
            cp = subprocess.run(
                ["bash", str(INSTALLER)],
                cwd=ROOT,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )

            self.assertEqual(cp.returncode, 0, cp.stderr)
            profile = home / ".bash_profile"
            self.assertTrue(profile.is_file())
            self.assertIn(str(bin_dir), profile.read_text(encoding="utf-8"))
            self.assertFalse((home / ".bashrc").exists())
            self.assertIn(".bash_profile", cp.stdout)


if __name__ == "__main__":
    unittest.main()
