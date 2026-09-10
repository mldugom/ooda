"""Pre-merge corrections: blocker consistency, challenge output, fact-scoped truth.

Each class covers one defect found in review of the vnext implementation.
"""

import itertools
import unittest

from ooda.policy import (
    BLOCKED_FOR,
    BLOCKER_TYPES,
    CHALLENGE_TAG,
    DEFAULT_FACT_DOMAIN,
    FACT_DOMAINS,
    INTENTS,
    Blocker,
    TruthClaim,
    blocker_challenge_required,
    challenge_line,
    parse_blocker,
    resolve_truth,
    truth_rank,
    work_permitted,
)


class TestBlockerConsistency(unittest.TestCase):
    """A serialized blocker may never contradict enforced permission.

    Before this fix, a data/environment/authority/promotion blocker whose
    blocked_for included exploration serialized exploration_allowed=True while
    work_permitted("explore") returned False.
    """

    def test_every_type_by_every_exploration_scope(self):
        for btype in BLOCKER_TYPES:
            for n in range(len(BLOCKED_FOR) + 1):
                for scopes in itertools.combinations(BLOCKED_FOR, n):
                    blocker = Blocker(blocker_type=btype, blocked_for=scopes)
                    with self.subTest(type=btype, blocked_for=scopes):
                        self.assertEqual(
                            blocker.exploration_allowed,
                            work_permitted(blocker, "explore").allowed,
                            "serialized field disagrees with enforcement",
                        )

    def test_to_dict_matches_enforcement(self):
        for btype in BLOCKER_TYPES:
            for scopes in ((), ("exploration",), ("exploration", "evidence"), ("capital",)):
                blocker = Blocker(blocker_type=btype, blocked_for=scopes)
                with self.subTest(type=btype, blocked_for=scopes):
                    self.assertEqual(
                        blocker.to_dict()["exploration_allowed"],
                        work_permitted(blocker, "explore").allowed,
                    )

    def test_the_specific_regression(self):
        """The four types that used to lie."""
        for btype in ("data", "environment", "authority", "promotion"):
            blocker = Blocker(blocker_type=btype, blocked_for=("exploration",))
            with self.subTest(type=btype):
                self.assertFalse(blocker.exploration_allowed)
                self.assertFalse(blocker.to_dict()["exploration_allowed"])

    def test_sequencing_never_blocks_even_when_it_claims_to(self):
        blocker = Blocker(blocker_type="sequencing", blocked_for=tuple(BLOCKED_FOR))
        self.assertTrue(blocker.exploration_allowed)
        for intent in INTENTS:
            self.assertTrue(work_permitted(blocker, intent).allowed)

    def test_round_trip_through_serialization_is_stable(self):
        for btype in BLOCKER_TYPES:
            blocker = Blocker(blocker_type=btype, blocked_for=("exploration", "evidence"))
            reparsed = parse_blocker(blocker.to_dict())
            with self.subTest(type=btype):
                self.assertEqual(blocker.exploration_allowed, reparsed.exploration_allowed)
                self.assertEqual(
                    reparsed.exploration_allowed,
                    work_permitted(reparsed, "explore").allowed,
                )


class TestBlockerChallengeOutput(unittest.TestCase):
    """The invariant is preserved; only its prose footprint shrinks."""

    def test_no_blocker_still_requires_the_challenge(self):
        """Intentional: NO ACTION with no blocker is also a false-negative risk."""
        self.assertTrue(blocker_challenge_required(None))

    def test_required_whenever_exploration_survives(self):
        self.assertTrue(blocker_challenge_required(Blocker("promotion", ("qualification",))))
        self.assertTrue(blocker_challenge_required(Blocker("sequencing")))

    def test_not_required_when_exploration_is_genuinely_closed(self):
        blocker = Blocker("scientific", ("exploration",), target="continuous MFE")
        self.assertFalse(blocker_challenge_required(blocker))

    def test_challenge_line_is_one_line(self):
        line = challenge_line(True, "score the already-joined price as a supplementary baseline")
        self.assertNotIn("\n", line)
        self.assertTrue(line.startswith(CHALLENGE_TAG))

    def test_challenge_line_does_not_restate_the_question(self):
        line = challenge_line(False, "target not identifiable")
        self.assertNotIn("?", line[len(CHALLENGE_TAG):])
        self.assertLess(len(line), 120)

    def test_skills_ask_for_one_line_not_a_section(self):
        from pathlib import Path
        root = Path(__file__).resolve().parents[1] / "src/ooda/resources"
        for rel in ("grok/skills/ooda-controller/SKILL.md", "grok/skills/ooda/SKILL.md"):
            text = (root / rel).read_text(encoding="utf-8")
            with self.subTest(skill=rel):
                self.assertIn("one line", text)
                self.assertIn("Cheap honest experiment available?", text)
                self.assertNotIn("mandatory, in writing", text)


class TestFactScopedTruth(unittest.TestCase):
    """No source type may globally outrank every other."""

    def test_runtime_wins_operational_facts(self):
        res = resolve_truth([
            TruthClaim("project_state", "collector paused"),
            TruthClaim("frozen_artifact", "collector expected running"),
            TruthClaim("runtime", "ACTIVE_WRITER"),
        ], "operational")
        self.assertEqual(res.winner.source, "runtime")
        self.assertIn("project_state", res.stale_sources)

    def test_git_wins_repository_facts(self):
        res = resolve_truth([
            TruthClaim("project_state", "on main"),
            TruthClaim("runtime", "process started from main"),
            TruthClaim("git", "on feature/broad-model"),
        ], "repository")
        self.assertEqual(res.winner.source, "git")
        self.assertEqual(res.winner.value, "on feature/broad-model")

    def test_frozen_artifact_wins_scientific_contract(self):
        """A later runtime or trace cannot retroactively change what was frozen."""
        res = resolve_truth([
            TruthClaim("runtime", "multiple_1h > 1.002"),
            TruthClaim("trace", "we have been using 1.002"),
            TruthClaim("frozen_artifact", "multiple_1h > 1"),
        ], "scientific_contract")
        self.assertEqual(res.winner.source, "frozen_artifact")
        self.assertEqual(res.winner.value, "multiple_1h > 1")
        self.assertIn("runtime", res.stale_sources)

    def test_verified_trace_wins_mission_outcome(self):
        res = resolve_truth([
            TruthClaim("runtime", "the model looks good"),
            TruthClaim("git", "branch merged"),
            TruthClaim("trace", "negative_finding: C2 did not beat C0"),
        ], "mission_outcome")
        self.assertEqual(res.winner.source, "trace")

    def test_no_source_wins_every_domain(self):
        """The defect being fixed: one global ranking."""
        winners = set()
        for domain in FACT_DOMAINS:
            claims = [TruthClaim(src, f"{src}-value") for src in
                      ("runtime", "git", "frozen_artifact", "trace", "project_state")]
            winners.add(resolve_truth(claims, domain).winner.source)
        self.assertGreater(len(winners), 1, "a single source still outranks globally")
        self.assertEqual(winners, {"runtime", "git", "frozen_artifact", "trace"})

    def test_derived_surfaces_never_win_any_domain(self):
        for domain in FACT_DOMAINS:
            for derived in ("dashboard", "project_view"):
                res = resolve_truth([
                    TruthClaim(derived, "green"),
                    TruthClaim("project_state", "orientation prose"),
                ], domain)
                with self.subTest(domain=domain, derived=derived):
                    self.assertEqual(res.winner.source, "project_state")

    def test_prose_never_outranks_an_authoritative_surface(self):
        for domain in FACT_DOMAINS:
            for authoritative in ("runtime", "git", "frozen_artifact", "trace"):
                with self.subTest(domain=domain, source=authoritative):
                    self.assertGreater(
                        truth_rank(authoritative, domain),
                        truth_rank("project_state", domain),
                    )

    def test_default_domain_is_operational_and_backward_compatible(self):
        self.assertEqual(DEFAULT_FACT_DOMAIN, "operational")
        res = resolve_truth([
            TruthClaim("project_state", "paused"),
            TruthClaim("runtime", "ACTIVE"),
        ])
        self.assertEqual(res.winner.source, "runtime")
        self.assertEqual(res.domain, "operational")

    def test_unknown_domain_is_rejected(self):
        with self.assertRaises(ValueError):
            resolve_truth([TruthClaim("runtime", "x")], "vibes")


if __name__ == "__main__":
    unittest.main()
