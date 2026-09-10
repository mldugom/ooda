"""Frozen regression cases from the vnext audit.

Each test names the real failure it prevents. These assert on deterministic
policy, not on model output, so they cannot drift with a prompt edit.
"""

import unittest

from ooda.charter import diff_charter, new_charter
from ooda.policy import (
    Blocker,
    TruthClaim,
    claim_permitted,
    consequence_class,
    descriptor_warranted,
    lens_budget_ok,
    parse_blocker,
    resolve_truth,
    validation_route,
    work_permitted,
)
from ooda.policy import project_state_warnings
from ooda.preflight import preflight


class Test01CryptoFalseBlock(unittest.TestCase):
    """R1D.3C not qualified must not stop broad exploratory modelling."""

    def setUp(self):
        self.blocker = Blocker(
            blocker_type="promotion",
            blocked_for=("qualification",),
            claim_ceiling="discovery",
            note="R1D.3C multi-regime qualification not ready",
        )

    def test_exploration_allowed(self):
        self.assertTrue(self.blocker.exploration_allowed)
        self.assertTrue(work_permitted(self.blocker, "explore"))

    def test_qualification_still_blocked(self):
        self.assertFalse(work_permitted(self.blocker, "claim_qualification"))

    def test_production_and_capital_still_blocked(self):
        self.assertFalse(claim_permitted("discovery", "promote_production"))
        self.assertFalse(claim_permitted("discovery", "deploy_capital"))

    def test_sequencing_is_never_a_dependency(self):
        seq = Blocker(blocker_type="sequencing", blocked_for=("evidence",),
                      note="R1D.4 follows R1D.3C")
        self.assertFalse(seq.is_real_dependency)
        self.assertTrue(work_permitted(seq, "explore"))
        # even a scope it nominally names cannot bite
        self.assertTrue(work_permitted(seq, "claim_evidence"))


class Test02TrueIdentifiabilityBlock(unittest.TestCase):
    """Continuous MFE is genuinely not identifiable; the refusal must hold."""

    def setUp(self):
        self.blocker = Blocker(
            blocker_type="scientific",
            blocked_for=("exploration", "evidence", "qualification"),
            claim_ceiling="n-a",
            target="continuous intrahorizon MFE/MAE",
            note="only entry plus five scheduled observations exist",
        )

    def test_target_is_blocked_for_everything(self):
        self.assertFalse(self.blocker.exploration_allowed)
        for intent in ("explore", "claim_evidence", "claim_qualification"):
            self.assertFalse(
                work_permitted(self.blocker, intent, target="continuous intrahorizon MFE/MAE"),
                f"{intent} must stay blocked",
            )

    def test_identifiable_alternative_remains_open(self):
        # The refusal is scoped to its target, so a different endpoint is free.
        self.assertTrue(
            work_permitted(self.blocker, "explore", target="+1h scheduled-cadence outcome")
        )


class Test03TenniskalB1(unittest.TestCase):
    """A named F1-vs-B1 test can be undefined while the programme is open."""

    def setUp(self):
        self.blocker = Blocker(
            blocker_type="data",
            blocked_for=("evidence",),
            claim_ceiling="evidence",
            target="B1 sportsbook consensus comparison",
            note="sportsbook coverage n=0",
        )

    def test_the_named_comparison_is_blocked(self):
        self.assertFalse(
            work_permitted(self.blocker, "claim_evidence", target="B1 sportsbook consensus comparison")
        )

    def test_research_programme_is_not_blocked(self):
        self.assertTrue(self.blocker.exploration_allowed)
        self.assertTrue(work_permitted(self.blocker, "explore"))

    def test_elo_versus_kalshi_is_available(self):
        # A data blocker on one baseline says nothing about a different one.
        self.assertTrue(
            work_permitted(self.blocker, "claim_evidence", target="Elo vs executable Kalshi price")
        )


class Test04StaleProjectState(unittest.TestCase):
    """Runtime beats prose; PROJECT_STATE gets flagged, not obeyed."""

    def test_runtime_wins_and_prose_is_flagged(self):
        res = resolve_truth([
            TruthClaim("project_state", "collector paused", "PROJECT_STATE.md"),
            TruthClaim("runtime", "ACTIVE_WRITER", "flock held, fresh clocks"),
        ])
        self.assertEqual(res.winner.source, "runtime")
        self.assertEqual(res.winner.value, "ACTIVE_WRITER")
        self.assertTrue(res.conflict)
        self.assertIn("project_state", res.stale_sources)

    def test_git_beats_prose_for_repository_truth(self):
        res = resolve_truth([
            TruthClaim("project_state", "on main"),
            TruthClaim("git", "on feature/x"),
        ])
        self.assertEqual(res.winner.source, "git")

    def test_dashboard_never_wins(self):
        res = resolve_truth([
            TruthClaim("dashboard", "green"),
            TruthClaim("trace", "negative_finding"),
        ])
        self.assertEqual(res.winner.source, "trace")


class Test05Authority(unittest.TestCase):
    """Promising research does not unlock merge, deploy, or capital."""

    def test_research_continues_under_authority_block(self):
        blocker = Blocker(blocker_type="authority", blocked_for=("capital",),
                          claim_ceiling="evidence")
        self.assertTrue(work_permitted(blocker, "explore"))
        self.assertTrue(work_permitted(blocker, "claim_evidence"))

    def test_capital_stays_blocked(self):
        blocker = Blocker(blocker_type="authority", blocked_for=("capital",),
                          claim_ceiling="evidence")
        self.assertFalse(work_permitted(blocker, "deploy_capital"))

    def test_evidence_ceiling_bars_qualification_claims(self):
        self.assertFalse(claim_permitted("evidence", "claim_qualification"))
        self.assertTrue(claim_permitted("evidence", "claim_evidence"))


class Test06SealedHoldout(unittest.TestCase):
    """Development proceeds; sealed evidence stays sealed."""

    def test_development_allowed_qualification_not(self):
        blocker = Blocker(blocker_type="promotion", blocked_for=("qualification",),
                          claim_ceiling="discovery", note="holdout sealed, development active")
        self.assertTrue(work_permitted(blocker, "explore"))
        self.assertFalse(work_permitted(blocker, "claim_qualification"))

    def test_sealed_evidence_interpretation_is_high_consequence(self):
        route = validation_route(["sealed_evidence_interpretation"])
        self.assertEqual(route.consequence, "high")
        self.assertEqual(route.independent_validator, "required")


class Test07TrivialEngineering(unittest.TestCase):
    """A one-line deterministic fix must not attract ceremony."""

    def test_no_validator_required(self):
        route = validation_route([])
        self.assertEqual(route.consequence, "low")
        self.assertEqual(route.independent_validator, "not_required")

    def test_descriptors_are_omitted_when_they_change_nothing(self):
        self.assertFalse(descriptor_warranted("researcher", changes_behavior=False))
        self.assertFalse(descriptor_warranted(None, changes_behavior=True))

    def test_zero_lenses_is_within_budget(self):
        ok, _ = lens_budget_ok([])
        self.assertTrue(ok)


class Test08HighConsequenceRuntime(unittest.TestCase):
    """Lean is not reckless: live locking work keeps every protection."""

    def test_runtime_safety_requires_independent_validation(self):
        route = validation_route(["runtime_safety", "live_data_mutation"])
        self.assertEqual(route.consequence, "high")
        self.assertEqual(route.independent_validator, "required")
        self.assertTrue(route.deterministic_checks)

    def test_one_high_signal_dominates_low_ones(self):
        self.assertEqual(consequence_class(["exploratory_research", "security_boundary"]), "high")


class Test09EnvironmentPreflight(unittest.TestCase):
    """Detect the missing host snapshot before the expensive mission."""

    def test_missing_host_data_is_detected(self):
        report = preflight(
            ["path:/operator-host/only/tape.sqlite"],
            route_to="the operator host",
        )
        self.assertFalse(report.satisfied)
        self.assertEqual(len(report.missing), 1)

    def test_handoff_names_a_route_not_a_shrug(self):
        report = preflight(["path:/nope.sqlite"], route_to="operator host bravo")
        handoff = report.handoff()
        self.assertIn("operator host bravo", handoff)
        self.assertIn("must run on", handoff)

    def test_host_service_cannot_be_self_certified(self):
        report = preflight(["host_service:collector"])
        self.assertFalse(report.satisfied)

    def test_satisfied_environment_passes(self):
        report = preflight(["command:python3"])
        self.assertTrue(report.satisfied)


class Test10TargetMoving(unittest.TestCase):
    """A disappointing model must not quietly buy an easier target."""

    def _charter(self, **over):
        base = dict(
            decision="trade or skip", target="multiple_1h > 1",
            why_target_matters="net of cost it is the P&L decision",
            decision_time="buy time", baseline="constant predictor",
            primary_metrics=["log loss", "Brier"], holdout="sealed 4,401",
            stop_rule="after C0/C1/C2", resource_budget="small",
        )
        base.update(over)
        return new_charter(**base)

    def test_target_change_requires_reorientation(self):
        change = diff_charter(self._charter(), self._charter(target="multiple_1h > 0.99"))
        self.assertTrue(change.requires_reorientation)
        self.assertIn("target", change.changed)

    def test_metric_and_holdout_changes_are_also_gated(self):
        for field, value in (("primary_metrics", ["accuracy"]), ("holdout", "none"),
                             ("baseline", "nothing"), ("decision_time", "after the fact")):
            with self.subTest(field=field):
                self.assertTrue(
                    diff_charter(self._charter(), self._charter(**{field: value})).requires_reorientation
                )

    def test_prose_edits_are_not_drift(self):
        change = diff_charter(self._charter(), self._charter(resource_budget="medium"))
        self.assertFalse(change.requires_reorientation)


class Test11SessionTopicDrift(unittest.TestCase):
    """One subject per worker session is stated in the hot path."""

    def test_fork_policy_is_in_both_skills(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1] / "src/ooda/resources/grok/skills"
        controller = (root / "ooda-controller/SKILL.md").read_text(encoding="utf-8")
        worker = (root / "ooda/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("One subject per session", controller)
        for text in (controller, worker):
            lowered = text.lower()
            self.assertIn("materially different idea", lowered)
            self.assertTrue("fork" in lowered or "later mission" in lowered)


class Test12LensCeremony(unittest.TestCase):
    """Ordinary bounded data-science work needs no routing vocabulary."""

    def test_no_descriptors_is_valid(self):
        from ooda.cli import validate_work_order
        wo = {
            "schema": "ooda/work-order/v1", "id": "x", "project_id": "p",
            "objective": "compute a baseline", "claim_level": "discovery",
            "authority": {},
        }
        self.assertEqual(validate_work_order(wo), [])

    def test_two_lenses_need_justification(self):
        ok, why = lens_budget_ok(["statistical", "model-risk"])
        self.assertFalse(ok)
        self.assertIn("justification", why)

    def test_four_lenses_are_never_warranted(self):
        ok, _ = lens_budget_ok(["a", "b", "c", "d"], justification="because")
        self.assertFalse(ok)


class Test13OptionalSpecialistLens(unittest.TestCase):
    """Routing vocabulary survives for domains where it genuinely helps."""

    def test_specialist_lens_can_be_selected(self):
        self.assertTrue(descriptor_warranted("market-microstructure", changes_behavior=True))

    def test_two_lenses_pass_with_a_concrete_reason(self):
        ok, why = lens_budget_ok(
            ["market-microstructure", "portfolio"],
            justification="live execution sizing against a thin book",
        )
        self.assertTrue(ok)
        self.assertIn("live execution", why)

    def test_vocabulary_is_still_documented(self):
        from pathlib import Path
        ref = (Path(__file__).resolve().parents[1]
               / "src/ooda/resources/reference/routing-vocabulary.md").read_text(encoding="utf-8")
        for lens in ("market-microstructure", "security-abuse", "reliability-systems", "portfolio"):
            self.assertIn(lens, ref)


class Test04bProjectStateHygiene(unittest.TestCase):
    """PROJECT_STATE is orientation, not an event log of mutable facts."""

    STALE = """# PROJECT_STATE
Goal: predict the +1h outcome.
Currently on branch feature/broad-model, PR #42 open.
Collector is paused.
Development population 14,308 rows.
"""

    CLEAN = """# PROJECT_STATE
Goal: improve the trade/skip decision at buy time.
Current decision: is there signal in buy-time features at all?
Current bottleneck: no baseline has been measured.
Claim ceiling: discovery. Sealed holdout untouched.
Next unknown: does C1 beat C0 on log loss?
Authoritative pointers: .ooda/charter.json, the tape health endpoint, Git.
"""

    def test_mutable_facts_are_flagged(self):
        warnings = project_state_warnings(self.STALE)
        reasons = " ".join(w.reason for w in warnings)
        self.assertIn("Git", reasons)
        self.assertIn("runtime", reasons)
        self.assertGreaterEqual(len(warnings), 3)

    def test_orientation_prose_is_not_flagged(self):
        self.assertEqual(project_state_warnings(self.CLEAN), [])

    def test_headings_and_code_blocks_are_ignored(self):
        self.assertEqual(project_state_warnings("# branch\n> PR #1\n```\nHEAD\n```\n"), [])


class TestBackwardCompatibility(unittest.TestCase):
    """Old traces carrying a bare `blocked` must keep loading."""

    def test_legacy_bare_blocked_parses(self):
        blocker = parse_blocker("blocked")
        self.assertEqual(blocker.blocker_type, "legacy")
        self.assertTrue(blocker.needs_retyping)

    def test_legacy_does_not_bar_exploration(self):
        self.assertTrue(work_permitted(parse_blocker("blocked"), "explore"))

    def test_legacy_bars_claims_until_retyped(self):
        for intent in ("claim_evidence", "claim_qualification", "deploy_capital"):
            self.assertFalse(work_permitted(parse_blocker("blocked"), intent))

    def test_absent_blocker_is_not_an_error(self):
        self.assertIsNone(parse_blocker(None))
        self.assertTrue(work_permitted(None, "explore"))


if __name__ == "__main__":
    unittest.main()
