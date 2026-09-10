from pathlib import Path
import re
import unittest


def flat(text: str) -> str:
    """Collapse line wrapping so assertions test meaning, not formatting."""
    return re.sub(r"\s+", " ", text).strip()


ROOT = Path(__file__).resolve().parents[1]
CONTROLLER = ROOT / "src/ooda/resources/grok/skills/ooda-controller/SKILL.md"


class DomainOrientationTests(unittest.TestCase):
    def test_controller_orients_on_decision_and_value(self):
        """The four orientation questions survived the lean rewrite.

        vnext folded the standalone `## Domain/value preflight` section into
        ORIENT and moved the long form to reference/predictive-science.md, but
        the questions themselves are load-bearing and must stay in the hot path.
        The thin-output pass later demoted the loop headings to internal
        subsections, so this asserts the questions survive -- not a heading level.
        """
        text = flat(CONTROLLER.read_text(encoding="utf-8"))
        for marker in (
            "Orient",
            "operator decision",
            "outcome actually matters",
            "current bottleneck",
            "highest-value unknown",
        ):
            self.assertIn(marker, text)

    def test_controller_still_demands_decision_served_for_consequential_work(self):
        text = flat(CONTROLLER.read_text(encoding="utf-8"))
        self.assertIn("decision served", text)
        self.assertIn("KEEP THINKING", text)

    def test_domain_doctrine_maps_into_existing_control_room_state(self):
        text = (ROOT / "docs/DOMAIN_DECISION_ORIENTATION.md").read_text(encoding="utf-8")
        self.assertIn("## Project view and Control Room mapping", text)
        self.assertIn("objective_ladder", text)
        self.assertIn("stakeholder_summary", text)

    def test_work_order_doctrine_has_decision_and_value_fields(self):
        text = (ROOT / "contracts/WORK_ORDER.md").read_text(encoding="utf-8")
        self.assertIn("why now", text.lower())
        self.assertIn("decision served", text.lower())


if __name__ == "__main__":
    unittest.main()
