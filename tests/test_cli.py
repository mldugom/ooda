import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.cli import (
    cmd_doctor,
    cmd_init,
    cmd_setup,
    cmd_work_order,
    parser,
    validate_project,
    validate_trace,
    validate_work_order,
)


class ContractTests(unittest.TestCase):
    def test_example_work_order(self):
        self.assertEqual(validate_work_order(json.loads(Path("examples/work-order.json").read_text())), [])

    def test_example_trace(self):
        self.assertEqual(validate_trace(json.loads(Path("examples/trace.json").read_text())), [])

    def test_project_examples(self):
        for path in Path("examples/projects").glob("*.json"):
            with self.subTest(path=path):
                self.assertEqual(validate_project(json.loads(path.read_text())), [])

    def test_too_many_lenses_fails(self):
        d = json.loads(Path("examples/work-order.json").read_text())
        d["lenses"] = ["boyd", "scientific", "statistical", "taleb"]
        self.assertTrue(any("three lenses" in e for e in validate_work_order(d)))

    def test_scaffold_creates_minimal_ooda_project_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            args = SimpleNamespace(
                path=tmp,
                project_id="example-app",
                project_class="software-product",
                scaffold=True,
                force=False,
            )
            self.assertEqual(cmd_init(args), 0)
            root = Path(tmp)
            for rel in (
                ".ooda/project.json",
                ".ooda/README.md",
                "README.md",
                "AGENTS.md",
                "PROJECT_STATE.md",
            ):
                self.assertTrue((root / rel).exists(), rel)
            self.assertTrue((root / ".ooda/work-orders").is_dir())
            self.assertTrue((root / ".ooda/traces").is_dir())
            self.assertEqual(validate_project(json.loads((root / ".ooda/project.json").read_text())), [])

    def test_scaffold_does_not_overwrite_existing_docs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "README.md").write_text("existing\n")
            args = SimpleNamespace(
                path=tmp,
                project_id="example-app",
                project_class="software-product",
                scaffold=True,
                force=False,
            )
            self.assertEqual(cmd_init(args), 0)
            self.assertEqual((root / "README.md").read_text(), "existing\n")

    def test_doctor_validates_one_contract_file(self):
        args = SimpleNamespace(target="examples/work-order.json", path=None)
        out = StringIO()
        with redirect_stdout(out):
            self.assertEqual(cmd_doctor(args), 0)
        self.assertIn("PASS examples/work-order.json", out.getvalue())

    def test_mission_defaults_output_from_generated_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = SimpleNamespace(
                objective_text="Implement one bounded slice",
                objective=None,
                role="engineer",
                profile="backend",
                lenses="reliability-systems",
                claim_level="n-a",
                project_id="example",
                id="TEST-01",
                max_turns=6,
                max_investigation_steps=8,
                output=str(root / ".ooda/work-orders/TEST-01.json"),
            )
            self.assertEqual(cmd_work_order(args), 0)
            data = json.loads((root / ".ooda/work-orders/TEST-01.json").read_text())
            self.assertEqual(data["objective"], "Implement one bounded slice")
            self.assertEqual(data["id"], "TEST-01")

    def test_python_cli_exposes_mission_alias(self):
        args = parser().parse_args(
            [
                "mission",
                "Inspect one bounded slice",
                "--role",
                "architect",
                "--profile",
                "backend",
                "--claim",
                "n-a",
            ]
        )
        self.assertEqual(args.command, "mission")
        self.assertEqual(args.objective_text, "Inspect one bounded slice")
        self.assertEqual(args.role, "architect")

    def test_setup_installs_packaged_grok_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict(os.environ, {"GROK_HOME": tmp}, clear=False):
                self.assertEqual(cmd_setup(SimpleNamespace(force=False)), 0)
            root = Path(tmp)
            for rel in (
                "skills/ooda/SKILL.md",
                "skills/ooda-controller/SKILL.md",
                "policies/EFFICIENT_AGENT.md",
                "skills/ooda/reference/predictive-science.md",
                "skills/ooda-controller/reference/blocker-semantics.md",
            ):
                self.assertTrue((root / rel).is_file(), rel)

    def test_skill_sources_are_not_duplicated(self):
        """providers/*/skills used to hold an editable copy that could drift past
        CI. src/ooda/resources is now the single source; nothing may shadow it."""
        self.assertFalse(Path("providers/grok/skills").exists())
        self.assertTrue(Path("src/ooda/resources/grok/skills/ooda/SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
