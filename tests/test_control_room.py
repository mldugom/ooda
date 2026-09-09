import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda.control_room import _session_context, render_html


class ControlRoomTests(unittest.TestCase):
    def _project(self, repo: Path, project_id="tenniskal"):
        return {
            "repo": repo,
            "project_id": project_id,
            "objective": "Preregister R7 without outcome access",
            "stage": "review",
            "claim": "evidence",
            "next_gate": "Integration Owner approves R7 preregistration",
            "stakeholder_summary": "R6 is frozen; R7 compute is not authorized.",
            "blockers": "Human gate only",
            "role": "architect",
            "profile": "quantitative-research",
            "work_order": "tk-r7-prereg",
            "result_state": "needs_human_gate",
            "controller": "needs human gate",
            "branch": "main",
            "head": "7c220a7",
            "dirty": "no",
            "updated": "2026-09-08 01:30",
            "objective_ladder": [
                {"status": "completed", "label": "Freeze ALPHA_HYPOTHESES_V1"},
                {"status": "current", "label": "Preregister R7"},
                {"status": "provisional", "label": "Run R7 under frozen protocol"},
            ],
            "timeline": [
                {
                    "at": "2026-09-08",
                    "decision": "Freeze five R7 market-state hypotheses",
                    "so_what": "R7 may test only frozen intensity, acceleration, and staleness definitions.",
                    "bigger_idea": "Tenniskal moves from exploration to preregistered predictive testing; outcome-driven feature changes remain unauthorized.",
                }
            ],
        }

    def test_renders_compact_control_surface_and_specific_timeline_labels(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            (repo / ".ooda").mkdir(parents=True)
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertIn("OODA Control Room", page)
        self.assertIn('class="ooda-rail"', page)
        self.assertIn("NOW", page)
        self.assertIn("WAITING ON / GATE", page)
        self.assertIn("NEXT IF CURRENT GATE PASSES", page)
        self.assertIn("OBJECTIVE LADDER", page)
        self.assertIn("MATERIAL DECISION TIMELINE", page)
        self.assertIn("IMMEDIATE CONSEQUENCE", page)
        self.assertIn("PROGRAM IMPACT", page)
        self.assertIn("FEEDBACK-LOOP EFFICIENCY", page)
        self.assertNotIn("LIVE OODA LOOP", page)
        self.assertIn("Not enough recorded mission economics yet (0/3)", page)
        self.assertIn("CURRENT MISSION", page)

    def test_project_sidebar_replaces_horizontal_tabs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            one = root / "tenniskal"
            two = root / "crypto-innout"
            (one / ".ooda").mkdir(parents=True)
            (two / ".ooda").mkdir(parents=True)
            page = render_html(
                [self._project(one, "tenniskal"), self._project(two, "crypto-innout")],
                15,
                root,
            )

        self.assertIn('class="project-sidebar"', page)
        self.assertIn('class="project-nav active"', page)
        self.assertIn('data-project-name="tenniskal"', page)
        self.assertIn('data-project-name="crypto-innout"', page)
        self.assertNotIn('class="project-tabs"', page)
        self.assertEqual(page.count('class="project-panel active"'), 1)
        self.assertIn("localStorage.setItem('ooda.activeProject'", page)

    def test_editorial_style_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            (repo / ".ooda").mkdir(parents=True)
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertIn("--bg:#f4eedc", page)
        self.assertIn("--paper:#fffdf7", page)
        self.assertIn("Georgia", page)
        self.assertIn("--accent:#4c78a8", page)
        self.assertNotIn("--bg:#0f1115", page)

    def test_grok_telemetry_renders_context_and_metered_session_cost(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            (repo / ".ooda").mkdir(parents=True)
            (repo / ".ooda/session-telemetry.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/session-telemetry/v1",
                        "provider": "grok",
                        "model": "Grok 4.6",
                        "context_used": 29000,
                        "context_limit": 500000,
                        "session_cost_usd": 0.37,
                        "session_cost_kind": "provider-metered",
                        "updated_at": "2026-09-08T01:30:00-04:00",
                    }
                )
            )
            telemetry = _session_context(repo)
            page = render_html([self._project(repo, "demo")], 15, Path(tmp))

        self.assertIsNotNone(telemetry)
        self.assertAlmostEqual(telemetry["pct"], 5.8)
        self.assertIn("5.8%", page)
        self.assertIn("29K / 500K", page)
        self.assertIn("$0.370 session", page)
        self.assertNotIn("~$0.370 session", page)

    def test_deepseek_telemetry_labels_estimate_and_actual_balance(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "demo"
            (repo / ".ooda").mkdir(parents=True)
            (repo / ".ooda/session-telemetry.json").write_text(
                json.dumps(
                    {
                        "schema": "ooda/session-telemetry/v1",
                        "provider": "deepseek",
                        "model": "deepseek-v4-pro",
                        "context_used": 84000,
                        "context_limit": 1000000,
                        "session_cost_usd": 0.07,
                        "session_cost_kind": "tui-estimate",
                        "account_balance": 9.62,
                        "account_currency": "USD",
                        "updated_at": "2026-09-08T01:30:00-04:00",
                    }
                )
            )
            page = render_html([self._project(repo, "demo")], 15, Path(tmp))

        self.assertIn("8.4%", page)
        self.assertIn("84K / 1.0M", page)
        self.assertIn("~$0.070 session", page)
        self.assertIn("USD 9.62 balance", page)

    def test_telemetry_register_absent_when_no_adapter_has_written_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            (repo / ".ooda").mkdir(parents=True)
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertNotIn("SESSION TELEMETRY", page)
        self.assertNotIn('<div class="context-card">', page)

    def test_efficiency_chart_hidden_below_three_missions(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            work_orders = repo / ".ooda" / "work-orders"
            traces = repo / ".ooda" / "traces"
            work_orders.mkdir(parents=True)
            traces.mkdir(parents=True)
            for i in range(2):
                wid = f"mission-{i}"
                (work_orders / f"{wid}.json").write_text(
                    json.dumps({"id": wid, "created_at": "2026-09-08T00:00:00Z"})
                )
                (traces / f"{wid}.json").write_text(
                    json.dumps(
                        {
                            "work_order_id": wid,
                            "completed_at": "2026-09-08T00:10:00Z",
                            "economics": {"cost_usd": 0.1},
                            "result": {"state": "completed"},
                        }
                    )
                )
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertNotIn('class="efficiency-chart"', page)
        self.assertIn("Not enough recorded mission economics yet (2/3)", page)

    def test_efficiency_chart_renders_at_three_missions(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            work_orders = repo / ".ooda" / "work-orders"
            traces = repo / ".ooda" / "traces"
            work_orders.mkdir(parents=True)
            traces.mkdir(parents=True)
            for i in range(3):
                wid = f"mission-{i}"
                (work_orders / f"{wid}.json").write_text(
                    json.dumps({"id": wid, "created_at": "2026-09-08T00:00:00Z"})
                )
                (traces / f"{wid}.json").write_text(
                    json.dumps(
                        {
                            "work_order_id": wid,
                            "completed_at": "2026-09-08T00:10:00Z",
                            "economics": {"cost_usd": 0.1},
                            "result": {"state": "completed"},
                        }
                    )
                )
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertIn('class="efficiency-chart"', page)
        self.assertNotIn("Not enough recorded mission economics yet", page)

    def test_needs_you_ordering_ranks_blocked_project_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            idle = root / "idle-project"
            blocked = root / "blocked-project"
            (idle / ".ooda").mkdir(parents=True)
            (blocked / ".ooda").mkdir(parents=True)
            idle_project = self._project(idle, "idle-project")
            idle_project["controller"] = "active"
            blocked_project = self._project(blocked, "blocked-project")
            blocked_project["controller"] = "blocked"
            page = render_html([idle_project, blocked_project], 15, root)

        first_tab = page.index('data-project-tab="0"')
        self.assertIn('data-project-name="blocked-project"', page[first_tab : first_tab + 200])

    def test_auto_refresh_has_pause_toggle_instead_of_meta_refresh(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "tenniskal"
            (repo / ".ooda").mkdir(parents=True)
            page = render_html([self._project(repo)], 15, Path(tmp))

        self.assertNotIn("http-equiv=\"refresh\"", page)
        self.assertIn('id="refresh-toggle"', page)
        self.assertIn("toggleAutoRefresh", page)


if __name__ == "__main__":
    unittest.main()
