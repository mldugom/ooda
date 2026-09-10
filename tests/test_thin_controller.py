"""Thin controller output contract and controller-scoped reference loading.

Grok telemetry showed cases 1-4 passing functionally but costing 12 turns and
~302k tokens, with the Tennis routing decision alone at 5 turns / ~139k. The
cause was presentation, not semantics: the controller printed its whole internal
scaffold and loaded a domain reference merely because the project was predictive.

These guards are structural, not prose-exact -- they assert the rules exist and
that the old broad trigger is gone, without pinning wording.
"""

import re
import unittest
from pathlib import Path

def flat(text: str) -> str:
    """Collapse line wrapping so assertions test meaning, not formatting."""
    return re.sub(r"\s+", " ", text).strip().lower()


ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "src/ooda/resources"
CONTROLLER = RES / "grok/skills/ooda-controller/SKILL.md"
WORKER = RES / "grok/skills/ooda/SKILL.md"


class TestReferenceLoading(unittest.TestCase):
    """A domain is not a trigger; a concrete ambiguity is."""

    def setUp(self):
        self.text = CONTROLLER.read_text(encoding="utf-8")
        self.section = self.text.split("## Load on demand")[1]

    def test_broad_predictive_trigger_is_gone(self):
        """The old rule loaded predictive-science for every predictive mission."""
        self.assertNotIn("any predictive/modelling mission", self.text)
        self.assertNotIn("any predictive or modelling mission", self.text)

    def test_predictive_reference_still_reachable(self):
        self.assertIn("predictive-science.md", self.section)
        self.assertTrue((RES / "reference/predictive-science.md").is_file())

    def test_loading_requires_a_statable_unresolved_question(self):
        """The rule must be mechanical: name the question or do not open the file."""
        lowered = flat(self.section)
        self.assertIn("cannot safely choose between", lowered)
        self.assertIn("if you cannot state that, do not open it", lowered)

    def test_confirmation_reads_are_named_and_forbidden(self):
        """Grok opened references "so the decision matches doctrine" -- a
        confirmation read that the earlier "concrete ambiguity" wording did not
        explicitly forbid."""
        lowered = flat(self.section)
        self.assertIn("never open one to confirm doctrine", lowered)
        for anti_pattern in ("raise confidence", "project is predictive",
                             "blocker word", "blocked stage", "prompt is a test"):
            self.assertIn(anti_pattern, lowered)

    def test_worker_may_still_load_predictive_science_normally(self):
        """Narrowing is controller-scoped; the worker doing the work is unaffected."""
        worker = WORKER.read_text(encoding="utf-8")
        self.assertIn("predictive-science.md", worker)
        self.assertIn("predictive", worker.split("## Load on demand")[1].lower())

    def test_every_named_reference_is_still_installed(self):
        from ooda.layout import SKILL_REFERENCES
        for name in re.findall(r"`([a-z-]+\.md)`", self.section):
            self.assertIn(name, SKILL_REFERENCES["ooda-controller"])


class TestOutputContract(unittest.TestCase):
    """The controller reasons through the loop but does not print it."""

    def setUp(self):
        self.text = CONTROLLER.read_text(encoding="utf-8")

    def test_a_print_contract_exists(self):
        self.assertIn("## What to print", self.text)

    def test_the_loop_is_marked_internal(self):
        self.assertIn("Reason internally", self.text)
        # The loop steps must not be top-level sections that read as a template.
        for step in ("Observe", "Orient", "Decide", "Act", "Re-observe"):
            self.assertNotIn(f"\n## {step.upper()}", self.text)
            self.assertNotIn(f"\n## {step} ", self.text)

    def test_scaffold_printing_is_forbidden(self):
        lowered = flat(self.text.split("## What to print")[1])
        self.assertIn("never print", lowered)
        self.assertTrue(
            "scaffold" in lowered or "observe/orient" in lowered,
            "the contract must name the scaffold it forbids",
        )

    def test_work_order_is_not_echoed_by_default(self):
        contract = flat(self.text.split("## What to print")[1])
        self.assertIn("work order", contract)
        self.assertIn("never echo", contract)

    def test_full_output_remains_available_on_request(self):
        """Narrowing the default must not remove the capability."""
        contract = flat(self.text.split("## What to print")[1])
        self.assertIn("only when the user asks", contract)
        self.assertTrue(
            "handoff" in contract or "audit" in contract,
            "the contract must say what a request can still produce",
        )

    def test_needing_to_act_is_not_a_reason_to_print_the_mission(self):
        """The old clause "or when the user must act on it themselves" was the
        escape hatch Grok used to print a whole work order."""
        contract = flat(self.text.split("## What to print")[1])
        self.assertNotIn("must act on it themselves", contract)
        self.assertIn("needing to act on it is not a reason", contract)

    def test_propose_mission_does_not_mean_print_the_mission(self):
        contract = flat(self.text.split("## What to print")[1])
        self.assertIn("does not print the mission body", contract)

    def test_default_shape_names_the_four_verbs(self):
        contract = self.text.split("## What to print")[1]
        for verb in ("KEEP THINKING", "PROPOSE MISSION", "HUMAN GATE", "BLOCK"):
            self.assertIn(verb, contract)

    def test_trivial_escape_survives(self):
        self.assertIn("## First: is this small?", self.text)
        head = self.text.split("## Reason internally")[0]
        self.assertIn("one or two lines", head)
        contract = self.text.split("## What to print")[1]
        self.assertIn("one or two lines", contract)


class TestSafeguardsUnchanged(unittest.TestCase):
    """Shorter answers must come from what is printed, never from what applies."""

    def setUp(self):
        self.text = CONTROLLER.read_text(encoding="utf-8")

    def test_block_still_requires_the_one_line_challenge(self):
        self.assertIn("Cheap honest experiment available?", self.text)
        challenge = flat(self.text.split("#### Blocker challenge")[1].split("###")[0])
        self.assertIn("mandatory", flat(self.text.split("#### Blocker challenge")[1][:80]))
        self.assertIn("propose it instead", challenge)

    def test_typed_blocker_fields_intact(self):
        for field in ("blocker_type", "blocked_for", "claim_ceiling", "exploration_allowed"):
            self.assertIn(field, self.text)

    def test_locality_route_still_names_location_command_artifact(self):
        contract = flat(self.text.split("## What to print")[1])
        self.assertIn("where to run", contract)
        self.assertIn("command", contract)
        self.assertIn("artifact", contract)

    def test_core_protections_still_present(self):
        lowered = self.text.lower()
        for rule in ("point-in-time", "sealed holdout", "never invent facts",
                     "human authority", "self-certification"):
            self.assertIn(rule, lowered)

    def test_truth_authority_and_stage_rules_survive(self):
        self.assertIn("frozen artifact", self.text)
        self.assertIn("Stages describe evidence", self.text)
        self.assertIn("claim ceiling is not a work ceiling", self.text)


if __name__ == "__main__":
    unittest.main()
