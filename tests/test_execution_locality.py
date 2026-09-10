"""Execution locality: data stays where it lives, code moves to the data.

Deterministic policy only -- no engine, no RPC, no scheduler. These assert the
routing decision and the reuse decision, which are the two things that must not
regress.
"""

import unittest

from ooda.policy import DerivedArtifact, artifact_reuse, contract_fingerprint
from ooda.preflight import HERE, Requirement, plan_execution, preflight

# The Tenniskal Phase 1 upstream contract, as frozen.
ELO_CONTRACT = {
    "source": "kalshi_owned_history",
    "elo": "R0=1500,K=32,scale=400",
    "filter": "R4uR5 two-contract, deduped",
    "pools": "men/women separate",
    "as_of": "2026-09-01",
}


class Test1LocalityRouting(unittest.TestCase):
    """Data on the operator host, absent here -> route, do not block."""

    def setUp(self):
        self.plan = plan_execution(
            [Requirement("path", "/operator-host/data/radar.sqlite", at="operator host")],
            entry_point="python -m alpha.research.broad_baseline --summary-json result.json",
            result_artifact="result.json",
        )

    def test_execution_routes_to_the_authoritative_location(self):
        self.assertFalse(self.plan.runs_here)
        self.assertEqual(self.plan.run_at, "operator host")

    def test_code_work_is_still_allowed_here(self):
        """Routing is not a research block."""
        self.assertTrue(self.plan.code_work_allowed)
        self.assertFalse(self.plan.data_work_allowed_here)

    def test_summary_names_one_command_and_one_artifact(self):
        summary = self.plan.summary()
        self.assertIn("operator host", summary)
        self.assertIn("python -m alpha.research.broad_baseline", summary)
        self.assertIn("result.json", summary)
        self.assertIn("fixtures", summary)

    def test_runs_here_when_everything_is_present(self):
        plan = plan_execution([Requirement("command", "python3")])
        self.assertTrue(plan.runs_here)
        self.assertEqual(plan.run_at, HERE)
        self.assertTrue(plan.data_work_allowed_here)


class Test2PythonFirst(unittest.TestCase):
    """A repeated, stable, deterministic workflow deserves one Python entry point."""

    def test_reference_states_the_preference_order(self):
        from pathlib import Path
        ref = (Path(__file__).resolve().parents[1]
               / "src/ooda/resources/reference/predictive-science.md").read_text(encoding="utf-8")
        self.assertIn("Python-first", ref)
        self.assertIn("thin launch glue", ref)
        self.assertIn("python -m alpha.research.broad_baseline", ref)

    def test_worker_skill_carries_the_rule(self):
        from pathlib import Path
        skill = (Path(__file__).resolve().parents[1]
                 / "src/ooda/resources/grok/skills/ooda/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Python-first", skill)
        self.assertIn("Shell is thin glue", skill)

    def test_a_collapsed_workflow_is_one_entry_point(self):
        """snapshot+validate+cohort+metrics+invariants+summary is one command."""
        plan = plan_execution(
            [Requirement("path", "data/tape.sqlite", at="operator host")],
            entry_point="python -m alpha.research.broad_baseline --snapshot data/tape.sqlite --summary-json result.json",
            result_artifact="result.json",
        )
        self.assertEqual(plan.entry_point.count("python -m"), 1)
        self.assertNotIn("&&", plan.entry_point)


class Test3NoWrapperCeremony(unittest.TestCase):
    """A trivial one-off does not earn an abstraction."""

    def test_no_entry_point_required(self):
        plan = plan_execution([Requirement("command", "python3")])
        self.assertEqual(plan.entry_point, "")
        self.assertTrue(plan.runs_here)
        self.assertIn("may run here", plan.summary())

    def test_summary_stays_short_without_ceremony(self):
        plan = plan_execution([])
        self.assertTrue(plan.report.satisfied)
        self.assertLess(len(plan.summary()), 200)

    def test_reference_says_trivial_commands_need_no_wrapper(self):
        from pathlib import Path
        ref = (Path(__file__).resolve().parents[1]
               / "src/ooda/resources/reference/predictive-science.md").read_text(encoding="utf-8")
        self.assertIn("does not need a wrapper", ref)


class Test4DerivedArtifactReuse(unittest.TestCase):
    """Reuse the authoritative derived artifact when the contract still holds."""

    def setUp(self):
        self.artifact = DerivedArtifact(
            "phase1 evaluation set", dict(ELO_CONTRACT), rows=1042,
            path="research/phase1_eval.parquet")

    def test_unchanged_contract_reuses(self):
        decision = artifact_reuse(self.artifact, dict(ELO_CONTRACT))
        self.assertTrue(decision)
        self.assertIn("1042 rows", decision.reason)

    def test_a_fresh_session_is_not_a_reason_to_recompute(self):
        decision = artifact_reuse(self.artifact, dict(ELO_CONTRACT))
        self.assertIn("fresh session is not a reason", decision.reason)

    def test_key_order_does_not_look_like_change(self):
        reordered = dict(reversed(list(ELO_CONTRACT.items())))
        self.assertTrue(artifact_reuse(self.artifact, reordered))
        self.assertEqual(contract_fingerprint(ELO_CONTRACT), contract_fingerprint(reordered))


class Test5UpstreamInvalidation(unittest.TestCase):
    """Never reuse silently once the contract moved."""

    def setUp(self):
        self.artifact = DerivedArtifact("phase1 evaluation set", dict(ELO_CONTRACT), rows=1042)

    def test_changed_contract_blocks_reuse_and_names_the_field(self):
        for field, value in (("elo", "R0=1500,K=24,scale=400"),
                             ("filter", "all rounds"),
                             ("source", "scraped_history"),
                             ("as_of", "2026-10-01")):
            with self.subTest(field=field):
                current = dict(ELO_CONTRACT); current[field] = value
                decision = artifact_reuse(self.artifact, current)
                self.assertFalse(decision)
                self.assertIn(field, decision.changed)
                self.assertIn("stale", decision.reason)

    def test_challenging_the_upstream_forces_recompute(self):
        decision = artifact_reuse(self.artifact, dict(ELO_CONTRACT), upstream_under_challenge=True)
        self.assertFalse(decision)
        self.assertIn("challenges how", decision.reason)

    def test_absent_artifact_is_computed_not_assumed(self):
        self.assertFalse(artifact_reuse(None, ELO_CONTRACT))


class Test6CompactEvidence(unittest.TestCase):
    """Bounded structured evidence, not bulk output."""

    def test_plan_names_the_result_artifact(self):
        plan = plan_execution(
            [Requirement("path", "data/x.sqlite", at="operator host")],
            entry_point="python -m alpha.research.broad_baseline",
            result_artifact="result.json")
        self.assertEqual(plan.to_dict()["result_artifact"], "result.json")
        self.assertIn("Return only", plan.summary())

    def test_plan_dict_is_small(self):
        plan = plan_execution([Requirement("path", "data/x.sqlite", at="operator host")])
        self.assertLessEqual(len(plan.to_dict()), 8)

    def test_hygiene_policy_is_stated(self):
        from pathlib import Path
        ref = (Path(__file__).resolve().parents[1]
               / "src/ooda/resources/reference/predictive-science.md").read_text(encoding="utf-8")
        for marker in ("summary.json", "SQL aggregate", "pytest -q", "every prediction"):
            self.assertIn(marker, ref)


class Test7CryptoRemoteEnvironment(unittest.TestCase):
    """Frozen regression: radar.sqlite is on the host, not in the remote agent."""

    def setUp(self):
        self.plan = plan_execution(
            [Requirement("path", "/nonexistent/radar.sqlite", at="operator host",
                         why="authoritative tape")],
            entry_point="python -m alpha.research.broad_baseline --snapshot data/radar.sqlite --summary-json result.json",
            result_artifact="result.json")

    def test_detected_before_any_expensive_work(self):
        self.assertFalse(self.plan.report.satisfied)
        self.assertEqual(len(self.plan.report.missing), 1)

    def test_code_preparation_allowed_evaluation_routed(self):
        self.assertTrue(self.plan.code_work_allowed)
        self.assertFalse(self.plan.data_work_allowed_here)
        self.assertEqual(self.plan.run_at, "operator host")

    def test_research_is_not_declared_blocked(self):
        summary = self.plan.summary().lower()
        self.assertNotIn("research is blocked", summary)
        self.assertIn("code may be written and tested here", summary)


class Test8TenniskalHistory(unittest.TestCase):
    """Frozen regression: do not replay ~38k matches for a downstream comparison."""

    def setUp(self):
        self.artifact = DerivedArtifact(
            "phase1 classifiable evaluation set", dict(ELO_CONTRACT), rows=1042)

    def test_downstream_comparison_reuses_the_1042_row_artifact(self):
        decision = artifact_reuse(self.artifact, dict(ELO_CONTRACT))
        self.assertTrue(decision, "must not replay the Elo history for a downstream comparison")
        self.assertIn("1042", decision.reason)

    def test_replay_only_when_elo_construction_is_challenged(self):
        decision = artifact_reuse(self.artifact, dict(ELO_CONTRACT),
                                  upstream_under_challenge=True)
        self.assertFalse(decision)

    def test_changed_elo_parameters_force_replay(self):
        current = dict(ELO_CONTRACT); current["elo"] = "R0=1500,K=16,scale=400"
        self.assertFalse(artifact_reuse(self.artifact, current))


class Test9ExistingVnextUnchanged(unittest.TestCase):
    """Locality is an addition; nothing from vnext may be reversed."""

    def test_preflight_signature_still_works(self):
        report = preflight(["command:python3"])
        self.assertTrue(report.satisfied)

    def test_requirements_without_a_location_still_parse(self):
        report = preflight([{"kind": "path", "value": "/nope"}, "command:python3"])
        self.assertFalse(report.satisfied)
        self.assertIn("must run on", report.handoff())

    def test_core_vnext_policy_is_intact(self):
        from ooda.policy import (Blocker, claim_permitted, resolve_truth,
                                 TruthClaim, validation_route, work_permitted)
        self.assertTrue(work_permitted(Blocker("sequencing", ("evidence",)), "claim_evidence"))
        self.assertFalse(claim_permitted("discovery", "claim_qualification"))
        self.assertEqual(
            resolve_truth([TruthClaim("project_state", "a"), TruthClaim("runtime", "b")]).winner.source,
            "runtime")
        self.assertEqual(validation_route(["capital"]).independent_validator, "required")


if __name__ == "__main__":
    unittest.main()
