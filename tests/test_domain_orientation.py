from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DomainOrientationTests(unittest.TestCase):
    def test_grok_controller_and_packaged_resource_match(self):
        provider = (ROOT / "providers/grok/skills/ooda-controller/SKILL.md").read_text(encoding="utf-8")
        packaged = (ROOT / "src/ooda/resources/grok/skills/ooda-controller/SKILL.md").read_text(encoding="utf-8")
        self.assertEqual(provider, packaged)

    def test_controller_has_domain_value_preflight(self):
        text = (ROOT / "providers/grok/skills/ooda-controller/SKILL.md").read_text(encoding="utf-8")
        for marker in (
            "## Domain/value preflight",
            "Decision served",
            "Value function",
            "Current bottleneck",
            "Critical path",
            "Information value",
            ".ooda/domain-decision-brief.md",
            "what decision does this serve, what bottleneck does it remove, and why now?",
        ):
            self.assertIn(marker, text)

    def test_domain_doctrine_maps_into_existing_control_room_state(self):
        text = (ROOT / "docs/DOMAIN_DECISION_ORIENTATION.md").read_text(encoding="utf-8")
        self.assertIn("## Project view and Control Room mapping", text)
        self.assertIn("objective_ladder", text)
        self.assertIn("stakeholder_summary", text)
        self.assertIn("Goal: <real value outcome>", text)
        self.assertIn("Current bottleneck:", text)
        self.assertIn("Why now:", text)

    def test_work_order_doctrine_has_decision_and_value_fields(self):
        text = (ROOT / "contracts/WORK_ORDER.md").read_text(encoding="utf-8")
        self.assertIn("decision served", text.lower())
        self.assertIn("value hypothesis", text.lower())


if __name__ == "__main__":
    unittest.main()
