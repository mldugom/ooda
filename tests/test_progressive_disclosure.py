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
        for skill in GROK_SKILLS:
            text = (RES / f"grok/skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            for named in referenced_files(text):
                self.assertIn(named, SKILL_REFERENCES[skill],
                              f"{skill} names {named} but the manifest does not ship it")

    def test_no_dead_docs_pointer_survives(self):
        for skill in GROK_SKILLS:
            text = (RES / f"grok/skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("docs/", text,
                             f"{skill} points at docs/ which is never installed")

    def test_manifest_has_no_orphan(self):
        named = set()
        for skill in GROK_SKILLS:
            text = (RES / f"grok/skills/{skill}/SKILL.md").read_text(encoding="utf-8")
            named.update(referenced_files(text))
        for ref in ALL_REFERENCES:
            self.assertIn(ref, named, f"{ref} is shipped but no skill names it")


class TestInstalledLayoutResolves(unittest.TestCase):
    def _install(self, home: Path, *, check: bool = True):
        env = dict(os.environ, GROK_HOME=str(home))
        return subprocess.run(
            ["bash", str(ROOT / "scripts/install-grok.sh")],
            check=check,
            env=env,
            capture_output=True,
            text=True,
        )

    def test_references_resolve_from_a_foreign_cwd(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "grokhome"
            self._install(home)
            unrelated = Path(tmp) / "some-other-project"
            unrelated.mkdir()
            cwd = os.getcwd()
            try:
                os.chdir(unrelated)
                for skill in GROK_SKILLS:
                    skill_dir = home / "skills" / skill
                    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                    for named in referenced_files(text):
                        resolved = skill_dir / "reference" / named
                        self.assertTrue(resolved.is_file(),
                                        f"{skill} -> reference/{named} is DEAD after install")
            finally:
                os.chdir(cwd)

    def test_pre_vnext_dangling_skill_links_are_migrated(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "grokhome"
            skills = home / "skills"
            skills.mkdir(parents=True)
            for skill in GROK_SKILLS:
                # This is the exact pre-vnext installation shape. The target no
                # longer exists on current main, so the symlink is dangling.
                (skills / skill).symlink_to(ROOT / "providers" / "grok" / "skills" / skill)

            proc = self._install(home)

            self.assertIn("Migrated legacy OODA skill link", proc.stdout)
            for skill in GROK_SKILLS:
                skill_dir = skills / skill
                self.assertFalse(skill_dir.is_symlink())
                self.assertTrue((skill_dir / "SKILL.md").is_file())
                self.assertTrue((skill_dir / "reference").is_dir())

    def test_unrelated_skill_symlink_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "grokhome"
            skills = home / "skills"
            target = Path(tmp) / "my-skill"
            target.mkdir()
            skills.mkdir(parents=True)
            link = skills / "ooda"
            link.symlink_to(target)

            proc = self._install(home, check=False)

            self.assertEqual(proc.returncode, 2)
            self.assertTrue(link.is_symlink())
            self.assertEqual(link.resolve(), target.resolve())
            self.assertIn("Refusing to replace unrelated skill symlink", proc.stderr)

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
        text = (RES / "grok/skills/ooda/SKILL.md").read_text(encoding="utf-8")
        head = text.split("## 1. Observe")[0]
        self.assertIn("Is this small?", head)
        self.assertNotIn("reference/", head)


class TestSingleSource(unittest.TestCase):
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
        sh = (ROOT / "scripts/install-grok.sh").read_text(encoding="utf-8")
        for skill, refs in SKILL_REFERENCES.items():
            line = [ln for ln in sh.split("\n") if ln.strip().startswith(f"{skill})")]
            self.assertTrue(line, f"install-grok.sh has no branch for {skill}")
            for ref in refs:
                self.assertIn(ref, line[0], f"install-grok.sh missing {ref} for {skill}")


if __name__ == "__main__":
    unittest.main()
