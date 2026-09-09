import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.domain_control_room import render_html


class DomainControlRoomTests(unittest.TestCase):
    def test_compact_domain_cockpit_promotes_value_orientation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "tenniskal"
            ooda = repo / ".ooda"
            ooda.mkdir(parents=True)
            (ooda / "domain-decision-brief.md").write_text(
                """# Domain decision brief\n\n## VALUE FUNCTION\nRepeatable positive after-fee EV on pre-match tennis.\n\n## DECISIONS\nTrade/skip; which side; executable price/time; size.\n\n## CURRENT BOTTLENECK\nNo signed fair-value probability independent of Kalshi.\n""",
                encoding="utf-8",
            )
            (ooda / "project-view.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/project-view/v1",
                        "objective_ladder": [
                            {"status": "completed", "label": "Trustworthy market tape"},
                            {"status": "current", "label": "Preregister PIT sportsbook consensus vs executable Kalshi"},
                            {"status": "provisional", "label": "Test simple signed-edge rule"},
                        ],
                        "timeline": [],
                        "stakeholder_summary": "Consensus is the cheapest first fair-P object; do not fit a tennis model yet.",
                    }
                ),
                encoding="utf-8",
            )
            project = {
                "repo": repo,
                "project_id": "tenniskal",
                "objective": "STALE: R7 preregistration",
                "stage": "review",
                "claim": "n-a",
                "next_gate": "Review fair-value preregistration",
                "stakeholder_summary": "Consensus is the cheapest first fair-P object; do not fit a tennis model yet.",
                "blockers": "Human gate",
                "controller": "needs human gate",
                "branch": "main",
                "head": "abc1234",
                "dirty": "no",
                "updated": "2026-09-09 14:00",
                "work_order": "tk-fair-value-prereg",
                "objective_ladder": [
                    {"status": "completed", "label": "Trustworthy market tape"},
                    {"status": "current", "label": "Preregister PIT sportsbook consensus vs executable Kalshi"},
                    {"status": "provisional", "label": "Test simple signed-edge rule"},
                ],
                "timeline": [],
            }
            page = render_html([project], 0, root)

        self.assertIn("domain-compact-control-room", page)
        self.assertIn("GOAL", page)
        self.assertIn("DECISION", page)
        self.assertIn("BOTTLENECK", page)
        self.assertIn("CURRENT MISSION", page)
        self.assertIn("WHY NOW", page)
        self.assertIn("Repeatable positive after-fee EV on pre-match tennis", page)
        self.assertIn("No signed fair-value probability independent of Kalshi", page)
        self.assertIn("VALUE CRITICAL PATH", page)
        self.assertIn("<details class=\"tech-details\"><summary>Technical state</summary>", page)
        self.assertIn("<p>STALE: R7 preregistration</p>", page)
        self.assertNotIn("VALUE CRITICAL PATH / CURRENT ORIENTATION", page)
        self.assertIn("HUMAN GATE", page)
        # The gate text must not also be repeated as a separate bottleneck/mission
        # card elsewhere on the page — that duplication was the PR #21 finding.
        self.assertEqual(page.count("Review fair-value preregistration"), 1)

    def test_missing_orientation_renders_explicit_unset_state_not_fabricated_prose(self):
        """Resilience fixture: a project with .ooda/project.json but no
        domain-decision-brief.md and no populated project-view orientation
        fields (a legitimate, common state — e.g. a freshly adopted repo, or
        a CI/sandbox checkout without the Integration Owner's local
        orientation artifacts). The Control Room must say so plainly instead
        of rendering fallback prose indistinguishable from a real answer."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "fresh-project"
            (repo / ".ooda").mkdir(parents=True)
            project = {
                "repo": repo,
                "project_id": "fresh-project",
                "objective": "No current objective recorded",
                "stage": "orient",
                "claim": "n-a",
                "next_gate": "No human/next gate recorded",
                "stakeholder_summary": "",
                "blockers": "",
                "controller": "idle",
                "branch": "main",
                "head": "0000000",
                "dirty": "no",
                "updated": "2026-09-09 00:00",
                "work_order": "—",
                "objective_ladder": [],
                "timeline": [],
            }
            page = render_html([project], 0, root)

        self.assertIn("Not yet recorded", page)
        self.assertNotIn("Goal not yet explicit — orient before consequential work", page)
        self.assertNotIn("Decision served not yet explicit", page)

    def test_grok_cost_telemetry_and_cost_guzzlers_render_when_present(self):
        from ooda.telemetry_ledger import record_snapshot
        from ooda.xai_usage import EXACT_API

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = root / "tenniskal"
            ooda = repo / ".ooda"
            (ooda / "work-orders").mkdir(parents=True)
            (ooda / "traces").mkdir(parents=True)
            (ooda / "work-orders" / "tk-r7-compute.json").write_text(
                json.dumps({"id": "tk-r7-compute"}), encoding="utf-8"
            )
            record_snapshot(
                repo,
                provider="grok",
                model="Grok 4.6",
                session_id="s1",
                cumulative_session_cost_usd=0.83,
                cumulative_session_cost_provenance=EXACT_API,
                usage={
                    "cost_in_usd_ticks": 8_300_000_000,
                    "prompt_tokens": 1000,
                    "prompt_tokens_details": {"cached_tokens": 760},
                    "completion_tokens": 120,
                },
            )
            (ooda / "session-telemetry.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/session-telemetry/v1",
                        "provider": "grok",
                        "model": "Grok 4.6",
                        "context_percent": 12.4,
                        "session_cost_usd": 0.83,
                        "effort": "high",
                        "effort_provenance": EXACT_API,
                        "current_mission_id": "tk-r7-compute",
                        "current_mission_attributed_spend_usd": 0.83,
                        "current_mission_attributed_spend_provenance": "LOCAL_DERIVED",
                        "last_request_usage": {
                            "cache_hit_pct": 76.0,
                            "cache_hit_pct_provenance": "LOCAL_DERIVED",
                            "reasoning_tokens": None,
                            "reasoning_tokens_provenance": "UNAVAILABLE",
                        },
                    }
                ),
                encoding="utf-8",
            )
            project = {
                "repo": repo,
                "project_id": "tenniskal",
                "objective": "R7 compute",
                "stage": "act",
                "claim": "evidence",
                "next_gate": "n/a",
                "stakeholder_summary": "",
                "blockers": "",
                "controller": "active",
                "branch": "main",
                "head": "abc1234",
                "dirty": "no",
                "updated": "2026-09-09 00:00",
                "work_order": "tk-r7-compute",
                "objective_ladder": [],
                "timeline": [],
            }
            page = render_html([project], 0, root)

        self.assertIn("SESSION TELEMETRY", page)
        self.assertIn("CURRENT MISSION ATTRIBUTED SPEND", page)
        self.assertIn("high", page)
        self.assertIn("$0.830", page)
        self.assertIn("76%", page)
        self.assertIn("COST GUZZLERS", page)
        self.assertIn("tk-r7-compute", page)
        self.assertIn(">SOURCE<", page)
        self.assertIn("Worker/child effort", page)


if __name__ == "__main__":
    unittest.main()
