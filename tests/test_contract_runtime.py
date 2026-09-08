import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import contract_runtime


class ContractRuntimeTests(unittest.TestCase):
    def test_work_order_gets_created_at(self):
        data = contract_runtime.enrich_contract({"schema": "ooda/work-order/v1", "id": "x"})
        self.assertIn("created_at", data)
        self.assertIn("+00:00", data["created_at"])

    def test_trace_gets_completed_at_and_explicit_cost(self):
        data = contract_runtime.enrich_contract(
            {"schema": "ooda/trace/v1", "economics": {"turns": 2, "cost_usd": None}},
            trace_cost_usd=0.18,
        )
        self.assertIn("completed_at", data)
        self.assertEqual(data["economics"]["cost_usd"], 0.18)
        self.assertEqual(data["economics"]["turns"], 2)

    def test_existing_timestamps_are_preserved(self):
        wo = contract_runtime.enrich_contract(
            {"schema": "ooda/work-order/v1", "created_at": "2026-01-01T00:00:00+00:00"}
        )
        trace = contract_runtime.enrich_contract(
            {"schema": "ooda/trace/v1", "completed_at": "2026-01-02T00:00:00+00:00"}
        )
        self.assertEqual(wo["created_at"], "2026-01-01T00:00:00+00:00")
        self.assertEqual(trace["completed_at"], "2026-01-02T00:00:00+00:00")

    def test_extract_cost_removes_compatibility_flag_before_argparse(self):
        argv = ["ooda", "trace", "--work-order", "x.json", "--cost-usd", "0.25"]
        value = contract_runtime._extract_trace_cost(argv)
        self.assertEqual(value, 0.25)
        self.assertNotIn("--cost-usd", argv)

    def test_negative_cost_is_rejected(self):
        argv = ["ooda", "trace", "--cost-usd", "-1"]
        with self.assertRaises(ValueError):
            contract_runtime._extract_trace_cost(argv)


if __name__ == "__main__":
    unittest.main()
