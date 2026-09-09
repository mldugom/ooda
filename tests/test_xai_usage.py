import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.xai_usage import (
    ESTIMATED,
    EXACT_API,
    LOCAL_DERIVED,
    PROVIDER_REPORTED,
    UNAVAILABLE,
    is_present,
    parse_usage,
    ticks_to_usd,
)


class XaiUsageTests(unittest.TestCase):
    def test_ticks_to_usd_exact_conversion(self):
        self.assertAlmostEqual(ticks_to_usd(8_300_000), 0.00083)
        self.assertAlmostEqual(ticks_to_usd(1e10), 1.0)

    def test_ticks_to_usd_missing_is_none(self):
        self.assertIsNone(ticks_to_usd(None))
        self.assertIsNone(ticks_to_usd("not-a-number"))

    def test_full_usage_payload_all_exact(self):
        usage = {
            "cost_in_usd_ticks": 8_300_000,
            "prompt_tokens": 1000,
            "prompt_tokens_details": {"cached_tokens": 400},
            "completion_tokens": 200,
            "completion_tokens_details": {"reasoning_tokens": 50},
            "total_tokens": 1200,
            "num_server_side_tools_used": 2,
            "service_tier": "default",
        }
        result = parse_usage(usage)

        self.assertAlmostEqual(result["cost_usd"], 0.00083)
        self.assertEqual(result["cost_usd_provenance"], EXACT_API)
        self.assertEqual(result["input_tokens"], 1000)
        self.assertEqual(result["cached_input_tokens"], 400)
        self.assertEqual(result["uncached_input_tokens"], 600)
        self.assertEqual(result["uncached_input_tokens_provenance"], LOCAL_DERIVED)
        self.assertEqual(result["output_tokens"], 200)
        self.assertEqual(result["reasoning_tokens"], 50)
        self.assertEqual(result["total_tokens"], 1200)
        self.assertEqual(result["server_tool_count"], 2)
        self.assertEqual(result["service_tier"], "default")
        self.assertAlmostEqual(result["cache_hit_pct"], 40.0)
        self.assertEqual(result["cache_hit_pct_provenance"], LOCAL_DERIVED)

    def test_missing_fields_are_unavailable_not_zero(self):
        result = parse_usage({"prompt_tokens": 500})

        self.assertIsNone(result["cost_usd"])
        self.assertEqual(result["cost_usd_provenance"], UNAVAILABLE)
        self.assertIsNone(result["cached_input_tokens"])
        self.assertEqual(result["cached_input_tokens_provenance"], UNAVAILABLE)
        self.assertIsNone(result["uncached_input_tokens"])
        self.assertIsNone(result["reasoning_tokens"])
        self.assertIsNone(result["cache_hit_pct"])
        self.assertEqual(result["cache_hit_pct_provenance"], UNAVAILABLE)

    def test_empty_or_missing_usage_is_all_unavailable(self):
        self.assertFalse(is_present(None))
        self.assertFalse(is_present({}))
        result = parse_usage(None)
        self.assertIsNone(result["cost_usd"])
        self.assertIsNone(result["input_tokens"])
        self.assertIsNone(result["service_tier"])

    def test_total_tokens_derived_when_not_supplied_directly(self):
        result = parse_usage({"prompt_tokens": 100, "completion_tokens": 40})
        self.assertEqual(result["total_tokens"], 140)
        self.assertEqual(result["total_tokens_provenance"], LOCAL_DERIVED)

    def test_alternate_key_names_are_read_defensively(self):
        result = parse_usage({"input_tokens": 10, "cached_input_tokens": 3, "output_tokens": 5})
        self.assertEqual(result["input_tokens"], 10)
        self.assertEqual(result["cached_input_tokens"], 3)
        self.assertEqual(result["output_tokens"], 5)

    def test_never_reports_estimated_provenance_from_this_parser(self):
        # This parser only ever produces EXACT_API, LOCAL_DERIVED, or
        # UNAVAILABLE — it has no source of estimates to report, and it
        # never emits PROVIDER_REPORTED (that category is for a runtime's
        # own self-report, e.g. Grok's effort/context/session-cost fields,
        # not for raw xAI usage-object parsing).
        result = parse_usage({"cost_in_usd_ticks": 1})
        provenances = {v for k, v in result.items() if k.endswith("_provenance")}
        self.assertTrue(provenances.issubset({EXACT_API, LOCAL_DERIVED, UNAVAILABLE}))
        self.assertNotIn(PROVIDER_REPORTED, provenances)
        self.assertNotIn(ESTIMATED, provenances)

    def test_provenance_taxonomy_has_five_distinct_categories(self):
        categories = {EXACT_API, PROVIDER_REPORTED, LOCAL_DERIVED, ESTIMATED, UNAVAILABLE}
        self.assertEqual(len(categories), 5)
        self.assertEqual(EXACT_API, "EXACT_API")
        self.assertEqual(PROVIDER_REPORTED, "PROVIDER_REPORTED")
        self.assertEqual(LOCAL_DERIVED, "LOCAL_DERIVED")
        self.assertEqual(ESTIMATED, "ESTIMATED")
        self.assertEqual(UNAVAILABLE, "UNAVAILABLE")


if __name__ == "__main__":
    unittest.main()
