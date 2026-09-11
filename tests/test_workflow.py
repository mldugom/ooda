import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import workflow


class WorkflowTests(unittest.TestCase):
    def _repo(self, root: Path) -> Path:
        repo = root / "crypto-innout"
        (repo / ".ooda").mkdir(parents=True)
        (repo / ".ooda/project.json").write_text(json.dumps({
            "schema": "ooda/project/v1",
            "project_id": "crypto-innout",
            "project_class": "trading-research",
            "authority": {"integration_owner": "human"},
        }))
        (repo / "PROJECT_STATE.md").write_text(
            "# Project State\n\n## Current objective\nTest wallet history against the market benchmark.\n\n"
            "## Open decisions / blockers\nNeed held-out economic evidence.\n\n"
            "## Next gate\nMeasure net value after realistic costs.\n"
        )
        return repo

    def _install_skill(self, grok_home: Path) -> None:
        for rel, body in workflow._expected_skill_files().items():
            path = grok_home / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)

    def test_skill_freshness_detects_stale_install_before_model_work(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "grok"
            self._install_skill(home)
            (home / "skills/ooda/SKILL.md").write_text("old skill")
            with mock.patch.dict(os.environ, {"GROK_HOME": str(home)}, clear=False):
                errors = workflow.skill_freshness_errors()
        self.assertTrue(any("stale" in error for error in errors))

    def test_run_uses_one_agent_by_default_and_records_exact_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            grok_home = root / "grok"
            ooda_home = root / "ooda-home"
            self._install_skill(grok_home)
            captured = []

            def fake_call(command):
                captured.append(command)
                session = workflow._session_root(repo) / "session-123"
                session.mkdir(parents=True)
                (session / "summary.json").write_text("{}")
                return 0

            with mock.patch.dict(os.environ, {"GROK_HOME": str(grok_home), "OODA_HOME": str(ooda_home)}, clear=False), \
                 mock.patch.object(workflow, "_grok_binary", return_value="/usr/local/bin/grok"), \
                 mock.patch.object(workflow.subprocess, "call", side_effect=fake_call):
                rc = workflow.run_work(repo, "Test one model comparison")
                stream = workflow._read_workstream(repo)

        self.assertEqual(rc, 0)
        self.assertNotIn("--subagents", captured[0])
        self.assertIn("--prompt", captured[0])
        self.assertEqual(stream["session_id"], "session-123")
        self.assertFalse(stream["allow_subagents"])

    def test_subagents_require_explicit_opt_in(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            grok_home = root / "grok"
            ooda_home = root / "ooda-home"
            self._install_skill(grok_home)
            captured = []

            def fake_call(command):
                captured.append(command)
                session = workflow._session_root(repo) / "session-456"
                session.mkdir(parents=True)
                return 0

            with mock.patch.dict(os.environ, {"GROK_HOME": str(grok_home), "OODA_HOME": str(ooda_home)}, clear=False), \
                 mock.patch.object(workflow, "_grok_binary", return_value="grok"), \
                 mock.patch.object(workflow.subprocess, "call", side_effect=fake_call):
                rc = workflow.run_work(repo, "Parallel specialist check", allow_subagents=True)

        self.assertEqual(rc, 0)
        self.assertIn("--subagents", captured[0])

    def test_continue_resumes_recorded_session_not_most_recent_guess(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            grok_home = root / "grok"
            ooda_home = root / "ooda-home"
            self._install_skill(grok_home)
            with mock.patch.dict(os.environ, {"GROK_HOME": str(grok_home), "OODA_HOME": str(ooda_home)}, clear=False):
                session = workflow._session_root(repo) / "ooda-session"
                session.mkdir(parents=True)
                workflow._write_workstream(repo, "ooda-session", allow_subagents=False)
                with mock.patch.object(workflow, "_grok_binary", return_value="grok"), \
                     mock.patch.object(workflow.subprocess, "call", return_value=0) as call:
                    rc = workflow.continue_work(repo)
                    command = call.call_args.args[0]

        self.assertEqual(rc, 0)
        self.assertIn("--resume", command)
        self.assertEqual(command[command.index("--resume") + 1], "ooda-session")
        self.assertNotIn("-c", command)

    def test_continue_refuses_session_from_older_framework_rules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            repo = self._repo(root)
            grok_home = root / "grok"
            ooda_home = root / "ooda-home"
            self._install_skill(grok_home)
            err = io.StringIO()
            with mock.patch.dict(os.environ, {"GROK_HOME": str(grok_home), "OODA_HOME": str(ooda_home)}, clear=False):
                session = workflow._session_root(repo) / "old-session"
                session.mkdir(parents=True)
                stream_path = workflow._workstream_path(repo)
                stream_path.parent.mkdir(parents=True)
                stream_path.write_text(json.dumps({
                    "schema": workflow.WORKSTREAM_SCHEMA,
                    "repo": str(repo.resolve()),
                    "session_id": "old-session",
                    "framework_fingerprint": "old-rules",
                    "allow_subagents": False,
                }))
                with mock.patch.object(workflow, "_grok_binary", return_value="grok"), \
                     mock.patch.object(workflow.subprocess, "call") as call, redirect_stderr(err):
                    rc = workflow.continue_work(repo)

        self.assertEqual(rc, 2)
        call.assert_not_called()
        self.assertIn("predates the current OODA rules", err.getvalue())

    def test_next_is_deterministic_and_does_not_launch_grok(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = self._repo(Path(tmp))
            out = io.StringIO()
            with mock.patch.object(workflow.subprocess, "call") as call, redirect_stdout(out):
                rc = workflow.print_next(repo)
        self.assertEqual(rc, 0)
        call.assert_not_called()
        text = out.getvalue()
        self.assertIn("Current question", text)
        self.assertIn("Next highest-value step", text)
        self.assertNotIn("C1", text)

    def test_help_exposes_only_small_everyday_surface_first(self):
        text = workflow.help_text()
        for command in ("ooda next", "ooda run", "ooda continue", "ooda check", "ooda dashboard"):
            self.assertIn(command, text)
        self.assertNotIn("route-validation", text)
        self.assertNotIn("charter --new", text)


if __name__ == "__main__":
    unittest.main()
