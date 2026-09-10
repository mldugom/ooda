"""Progressive disclosure must actually resolve after installation.

Pre-vnext, both skills pointed at `docs/X.md` files that no installer shipped,
so every pointer was dead from any real project working directory. These tests
make that state unreachable.
"""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ooda.layout import ALL_REFERENCES, GROK_SKILLS, SKILL_REFERENCES, referenced_files

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "src/ooda/resources"


class TestReferencesExist(unittest.TestCase):
    def test_every_manifest_reference_exists_in_the_repo(self):
        for ref in ALL_REFERENCES:
            self.assertTrue((RES / "reference" / ref).is_file(), f"missing source: {ref}")

    def test_every_reference_a_skill_names_is_in_its_manifest(self):
        """No skill may name a reference the installer does not ship."""
        for skill in GROK_SKILLS:
            text = (RES / f"grok/skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            for named in referenced_files(text):
                self.assertIn(named, SKILL_REFERENCES[skill],
                              f"{skill} names {named} but the manifest does not ship it")

    def test_no_dead_docs_pointer_survives(self):
        """The old `see docs/X.md` form must not come back."""
        for skill in GROK_SKILLS:
            text = (RES / f"grok/skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("docs/", text,
                             f"{skill} points at docs/ which is never installed")

    def test_manifest_has_no_orphan(self):
        """Every shipped reference is named by at least one skill."""
        named = set()
        for skill in GROK_SKILLS:
            text = (RES / f"grok/skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            named.update(referenced_files(text))
        for ref in ALL_REFERENCES:
            self.assertIn(ref, named, f"{ref} is shipped but no skill names it")


class TestInstalledLayoutResolves(unittest.TestCase):
    """Install for real, then resolve every pointer from an unrelated cwd."""

    def _install(self, home: Path):
        env = dict(os.environ, GROK_HOME=str(home))
        subprocess.run(["bash", str(ROOT / "scripts/install-grok.sh")],
                       check=True, env=env, capture_output=True)

    def test_references_resolve_from_a_foreign_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "grokhome"
            self._install(home)
            unrelated = Path(tmp) / "some-other-project"
            unrelated.mkdir()
            cwd = os.getcwd()
            try:
                os.chdir(unrelated)  # a normal project cwd, nothing to do with OODA
                for skill in GROK_SKILLS:
                    skill_dir = home / "skills" / skill
                    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                    for named in referenced_files(text):
                        resolved = skill_dir / "reference" / named
                        self.assertTrue(resolved.is_file(),
                                        f"{skill} -> reference/{named} is DEAD after install")
            finally:
                os.chdir(cwd)

    def test_cli_setup_installs_the_same_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "grokhome"
            env = dict(os.environ, GROK_HOME=str(home), PYTHONPATH=str(ROOT / "src"))
            proc = subprocess.run([sys.executable, "-m", "ooda.cli", "setup"],
                                  env=env, capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            for skill in GROK_SKILLS:
                for ref in SKILL_REFERENCES[skill]:
                    self.assertTrue((home / "skills" / skill / "reference" / ref).is_file(),
                                    f"ooda setup did not install {skill}/reference/{ref}")

    def test_trivial_work_does_not_need_a_reference(self):
        """The small-task short-circuit must sit before any reference trigger."""
        text = (RES / "grok/skills/ooda/SKILL.md").read_text(encoding="utf-8")
        head = text.split("## 1. Observe")[0]
        self.assertIn("Is this small?", head)
        self.assertNotIn("reference/", head)


class TestSingleSource(unittest.TestCase):
    """One editable copy of every skill; drift must be impossible, not merely detected."""

    def test_no_duplicate_skill_files_outside_resources(self):
        strays = [p for p in ROOT.rglob("SKILL.md")
                  if "src/ooda/resources" not in p.as_posix()
                  and ".git" not in p.as_posix()]
        self.assertEqual(strays, [], f"duplicate skill sources can drift: {strays}")

    def test_no_duplicate_reference_files(self):
        refs = [p for p in ROOT.rglob("*.md")
                if p.parent.name == "reference" and ".git" not in p.as_posix()]
        names = [p.name for p in refs]
        self.assertEqual(sorted(names), sorted(set(names)), "duplicate reference sources")

    def test_no_doc_duplicates_a_reference_body(self):
        """Copying reference prose into docs/ recreates the drift this replaced."""
        for ref in (RES / "reference").glob("*.md"):
            body = ref.read_text(encoding="utf-8")
            fingerprint = max(body.split("\n\n"), key=len).strip()[:120]
            for doc in (ROOT / "docs").glob("*.md"):
                self.assertNotIn(fingerprint, doc.read_text(encoding="utf-8"),
                                 f"{doc.name} duplicates {ref.name}; link to it instead")

    def test_packaging_ships_the_references(self):
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("resources/reference/*.md", pyproject)

    def test_shell_and_python_manifests_agree(self):
        """install-grok.sh and layout.py must ship the same set."""
        sh = (ROOT / "scripts/install-grok.sh").read_text(encoding="utf-8")
        for skill, refs in SKILL_REFERENCES.items():
            line = [ln for ln in sh.split("\n") if ln.strip().startswith(f"{skill})")]
            self.assertTrue(line, f"install-grok.sh has no branch for {skill}")
            for ref in refs:
                self.assertIn(ref, line[0], f"install-grok.sh missing {ref} for {skill}")


if __name__ == "__main__":
    unittest.main()
