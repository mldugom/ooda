"""Hot-path size guard.

The controller grew to ~3,750-4,911 token-equivalents before vnext, which is
what pushed doctrine out of the hot path and into files nothing installed.
Budgets are deliberately loose enough not to fail on wording tweaks, and tight
enough that another few hundred lines of prose cannot land unnoticed.
"""

import unittest
from pathlib import Path

from ooda.tokens import estimate

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "src/ooda/resources"

# (path, lo budget, hi budget)
BUDGETS = [
    (RES / "grok/skills/ooda-controller/SKILL.md", 1700, 2100),
    (RES / "grok/skills/ooda/SKILL.md", 1350, 1650),
    # Grew deliberately at vnext: the worker context budget and one-subject-per-
    # session rules were added, net of trimming doctrine the skills now carry.
    (RES / "EFFICIENT_AGENT.md", 1600, 2000),
]

# Pre-vnext measurements, for the reduction assertion and the record.
BASELINE = {
    "ooda-controller": (3750, 4911),
    "ooda": (1912, 2533),
}


class TestHotPathBudget(unittest.TestCase):
    def test_each_hot_path_file_is_within_budget(self):
        for path, lo_max, hi_max in BUDGETS:
            with self.subTest(file=path.name):
                lo, hi = estimate(path.read_text(encoding="utf-8"))
                self.assertLessEqual(lo, lo_max, f"{path.name} lo={lo} exceeds {lo_max}")
                self.assertLessEqual(hi, hi_max, f"{path.name} hi={hi} exceeds {hi_max}")

    def test_controller_is_materially_smaller_than_before(self):
        text = (RES / "grok/skills/ooda-controller/SKILL.md").read_text(encoding="utf-8")
        lo, _ = estimate(text)
        base_lo = BASELINE["ooda-controller"][0]
        reduction = 1 - lo / base_lo
        self.assertGreater(reduction, 0.45, f"controller reduction only {reduction:.0%}")

    def test_worker_is_not_larger_than_before(self):
        text = (RES / "grok/skills/ooda/SKILL.md").read_text(encoding="utf-8")
        lo, _ = estimate(text)
        self.assertLess(lo, BASELINE["ooda"][0])

    def test_references_are_not_in_the_hot_path(self):
        """Conditional doctrine must stay out of the always-loaded surface."""
        controller = (RES / "grok/skills/ooda-controller/SKILL.md").read_text(encoding="utf-8")
        for ref in (RES / "reference").glob("*.md"):
            body = ref.read_text(encoding="utf-8")
            # A reference is loaded on demand; its body must not be inlined.
            longest = max(body.split("\n\n"), key=len)
            self.assertNotIn(longest.strip()[:120], controller)

    def test_estimator_is_deterministic_and_offline(self):
        text = "the quick brown fox " * 50
        self.assertEqual(estimate(text), estimate(text))


if __name__ == "__main__":
    unittest.main()
