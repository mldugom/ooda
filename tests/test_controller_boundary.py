"""Controller/worker boundary.

The controller routes; the worker does domain reasoning. Clean sequential Grok
runs still showed the thin manager behaving like the researcher: opening domain
references to confirm rules already in its hot path, opening references that
carry project-specific worked answers, and constructing a full worker mission for
a question that only asked which control decision comes next.

These guards assert the boundary structurally -- the rules exist, the escalation
path exists, and the installed general-purpose doctrine no longer carries literal
answers to this project's regression cases. They do not pin wording.
"""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "src/ooda/resources"
CONTROLLER = RES / "grok/skills/ooda-controller/SKILL.md"
WORKER = RES / "grok/skills/ooda/SKILL.md"
REFERENCE = RES / "reference"

DOMAIN_REFERENCES = (
    "predictive-science.md",
    "blocker-semantics.md",
    "validation-routing.md",
    "visualization.md",
    "routing-vocabulary.md",
)


def flat(text: str) -> str:
    """Collapse line wrapping so assertions test meaning, not formatting."""
    return re.sub(r"\s+", " ", text).strip().lower()


class TestOrdinaryRoutingOpensNothing(unittest.TestCase):
    """Requirement A: a routing question is decided from the hot path alone."""

    def setUp(self):
        self.text = CONTROLLER.read_text(encoding="utf-8")
        self.section = flat(self.text.split("## Load on demand")[1])

    def test_ordinary_routing_is_stated_to_open_no_reference(self):
        self.assertIn("ordinary routing opens nothing", self.section)

    def test_the_ordinary_routing_questions_are_named(self):
        """A general rule the model must infer is weaker than named cases."""
        for question in ("control decision", "what happens next",
                         "is this blocked", "which mission runs"):
            self.assertIn(question, self.section)

    def test_the_hot_path_claims_to_be_sufficient_for_them(self):
        self.assertIn("every invariant they need is above", self.section)

    def test_every_forbidden_trigger_is_named(self):
        for trigger in ("confirm doctrine", "raise confidence",
                        "project is predictive", "blocker word", "blocker type",
                        "blocked stage", "prompt is hard", "prompt is a test",
                        "analogous worked case", "expected next experiment"):
            self.assertIn(trigger, self.section)


class TestUncertaintyEscalatesInsteadOfSelfResearch(unittest.TestCase):
    """Requirement A, second half: genuine uncertainty must not turn the
    controller into the worker."""

    def setUp(self):
        self.section = flat(CONTROLLER.read_text(encoding="utf-8").split("## Load on demand")[1])

    def test_escalation_is_the_named_alternative_to_researching(self):
        self.assertIn("escalate", self.section)
        self.assertIn("do not research", self.section)

    def test_both_escalation_routes_are_offered(self):
        self.assertIn("keep thinking", self.section)
        self.assertIn("orientation worker", self.section)

    def test_the_worker_not_the_controller_reads_the_reference(self):
        self.assertIn("you do not become the worker", self.section)


class TestWorkOrderIsOnlyForDispatch(unittest.TestCase):
    """Requirement B: a control query does not require the WORK_ORDER fields."""

    def setUp(self):
        self.text = CONTROLLER.read_text(encoding="utf-8")
        self.act = flat(self.text.split("### Act")[1].split("### Re-observe")[0])
        self.contract = flat(self.text.split("## What to print")[1])

    def test_payload_construction_is_conditioned_on_an_actual_dispatch(self):
        self.assertIn("only when you actually dispatch a child", self.act)

    def test_the_payload_goes_to_the_child_not_the_user(self):
        self.assertIn("to the child, not to the user", self.act)

    def test_a_control_question_is_explicitly_not_a_dispatch(self):
        self.assertIn("answering a control question is not a dispatch", self.act)
        self.assertIn("do not construct these fields", self.act)

    def test_the_default_printed_shape_carries_no_work_order_field(self):
        default = self.contract.split("locality adds")[0]
        for field in ("objective", "why now", "authoritative inputs",
                      "critical facts", "allowed", "forbidden",
                      "expected output", "stop condition"):
            self.assertNotIn(field, default, f"{field!r} leaked into the default shape")

    def test_the_full_artifact_is_still_available_on_request(self):
        """Narrowing the default must not remove the capability."""
        self.assertIn("only when the user asks", self.contract)
        self.assertTrue(
            "mission" in self.contract and
            ("handoff" in self.contract or "audit" in self.contract),
            "an explicit request must still produce the full artifact",
        )


class TestHotPathRetainsTheAntiFalseBlockInvariants(unittest.TestCase):
    """The boundary change fails if any rule that prevented the original false
    blocks now lives only in a reference the controller may no longer open."""

    def setUp(self):
        self.text = flat(CONTROLLER.read_text(encoding="utf-8"))

    def test_1_stage_is_evidence_not_permission(self):
        self.assertIn("stages describe evidence, never permission", self.text)
        self.assertIn("does not block the next", self.text)

    def test_2_claim_ceiling_is_not_a_work_ceiling(self):
        self.assertIn("a claim ceiling is not a work ceiling", self.text)

    def test_3_missing_comparator_scopes_to_its_own_claims(self):
        self.assertIn("missing comparator blocks only the claims needing it", self.text)
        self.assertIn("never the surrounding programme", self.text)

    def test_4_non_identifiability_binds_only_its_named_target(self):
        self.assertIn("binds only its named target", self.text)
        self.assertIn("which identifiable endpoint", self.text)

    def test_5_unreachable_environment_routes_rather_than_invalidates(self):
        self.assertIn("unreachable environment routes work", self.text)
        self.assertIn("never makes the scientific question invalid", self.text)

    def test_6_cheap_honest_experiment_challenge_precedes_declining(self):
        self.assertIn("cheap honest experiment available?", self.text)
        self.assertIn("propose it instead of declining", self.text)

    def test_7_holdout_pit_and_human_authority_survive(self):
        for rule in ("point-in-time", "sealed holdout", "never invent facts",
                     "explicit human authority", "self-certification"):
            self.assertIn(rule, self.text)


class TestReferencesCarryNoProjectAnswerKeys(unittest.TestCase):
    """Requirement C: installed general-purpose doctrine is reusable doctrine,
    not a stored answer to this repository's regression cases."""

    def setUp(self):
        self.installed = {p.name: p.read_text(encoding="utf-8")
                          for p in REFERENCE.glob("*.md")}
        self.installed["ooda-controller/SKILL.md"] = CONTROLLER.read_text(encoding="utf-8")
        self.installed["ooda/SKILL.md"] = WORKER.read_text(encoding="utf-8")

    def test_no_benchmark_case_identifier_appears(self):
        """Project names, stage labels, and case-specific quantities."""
        forbidden = ("Tenniskal", "Crypto-Innout", "Kalshi", "Elo",
                     "sportsbook", "Sportsbook", "R1D", "MFE",
                     "1,042", "38k", "C0/C1/C2", "13411")
        for name, body in self.installed.items():
            for token in forbidden:
                self.assertNotIn(token, body, f"{token!r} is a case answer key, found in {name}")

    def test_the_generic_scientific_rules_survive(self):
        """Generalizing examples must not gut the rule they illustrated."""
        blockers = flat(self.installed["blocker-semantics.md"])
        self.assertIn("comparator source never joined", blockers)
        self.assertIn("path-dependent quantity", blockers)
        self.assertIn("sparse snapshots", blockers)
        self.assertIn("no, for that target only", blockers)

        science = flat(self.installed["predictive-science.md"])
        self.assertIn("expensive replay already produced a frozen evaluation set", science)
        self.assertIn("reads that set", science)
        self.assertIn("construction of the artifact itself", science)

    def test_narrow_scope_doctrine_survives_without_the_case(self):
        blockers = flat(self.installed["blocker-semantics.md"])
        self.assertIn("single named comparison can be genuinely undefined", blockers)
        self.assertIn("record the narrow truth", blockers)


class TestReferencesRemainAvailableToWorkers(unittest.TestCase):
    """Narrowing is controller-scoped. The worker that does the reasoning keeps
    its doctrine."""

    def test_every_domain_reference_is_still_installed_and_non_empty(self):
        for name in DOMAIN_REFERENCES:
            path = REFERENCE / name
            self.assertTrue(path.is_file(), f"{name} was removed")
            self.assertGreater(len(path.read_text(encoding="utf-8").strip()), 200, name)

    def test_the_worker_still_loads_predictive_science(self):
        worker = WORKER.read_text(encoding="utf-8")
        self.assertIn("predictive-science.md", worker.split("## Load on demand")[1])

    def test_the_controller_can_still_reach_them_when_the_test_is_met(self):
        section = CONTROLLER.read_text(encoding="utf-8").split("## Load on demand")[1]
        for name in DOMAIN_REFERENCES:
            self.assertIn(name, section)

    def test_named_references_resolve_to_installed_files(self):
        from ooda.layout import SKILL_REFERENCES
        section = CONTROLLER.read_text(encoding="utf-8").split("## Load on demand")[1]
        for name in re.findall(r"`reference/([a-z-]+\.md)`", section):
            self.assertIn(name, SKILL_REFERENCES["ooda-controller"])


if __name__ == "__main__":
    unittest.main()
