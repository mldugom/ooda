import json, sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.cli import validate_project, validate_work_order, validate_trace

class ContractTests(unittest.TestCase):
    def test_example_work_order(self):
        self.assertEqual(validate_work_order(json.loads(Path("examples/work-order.json").read_text())), [])
    def test_example_trace(self):
        self.assertEqual(validate_trace(json.loads(Path("examples/trace.json").read_text())), [])
    def test_project_examples(self):
        for path in Path("examples/projects").glob("*.json"):
            with self.subTest(path=path): self.assertEqual(validate_project(json.loads(path.read_text())), [])
    def test_too_many_lenses_fails(self):
        d=json.loads(Path("examples/work-order.json").read_text()); d["lenses"]=["boyd","scientific","statistical","taleb"]
        self.assertTrue(any("three lenses" in e for e in validate_work_order(d)))
if __name__=="__main__": unittest.main()
