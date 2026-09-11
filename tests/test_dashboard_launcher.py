import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from ooda import dashboard_launcher


class DashboardLauncherTests(unittest.TestCase):
    def test_reuses_matching_ooda_dashboard(self):
        root = Path("/tmp/repos")
        with mock.patch.object(dashboard_launcher, "_is_ooda_dashboard", return_value=True), mock.patch.object(
            dashboard_launcher, "_port_open"
        ) as port_open:
            port, reuse = dashboard_launcher._select_port(8792, root)
        self.assertEqual((port, reuse), (8792, True))
        port_open.assert_not_called()

    def test_skips_foreign_service_on_preferred_port(self):
        root = Path("/tmp/repos")
        with mock.patch.object(dashboard_launcher, "_is_ooda_dashboard", return_value=False), mock.patch.object(
            dashboard_launcher, "_port_open", side_effect=lambda port: port == 8792
        ):
            port, reuse = dashboard_launcher._select_port(8792, root)
        self.assertEqual((port, reuse), (8793, False))

    def test_finds_existing_ooda_dashboard_after_foreign_port(self):
        root = Path("/tmp/repos")
        with mock.patch.object(
            dashboard_launcher, "_is_ooda_dashboard", side_effect=lambda port, _root: port == 8793
        ), mock.patch.object(dashboard_launcher, "_port_open", side_effect=lambda port: port == 8792):
            port, reuse = dashboard_launcher._select_port(8792, root)
        self.assertEqual((port, reuse), (8793, True))

    def test_current_generation_requires_stakeholder_markers(self):
        root = Path("/tmp/repos")
        current = (
            "<title>OODA Control Room</title> /tmp/repos "
            "stakeholder-dashboard business-objective technical-details"
        )
        previous = (
            "<title>OODA Control Room</title> /tmp/repos "
            "project-sidebar human-gate-band domain-compact-control-room"
        )
        with mock.patch.object(dashboard_launcher, "_dashboard_body", return_value=current):
            self.assertTrue(dashboard_launcher._is_ooda_dashboard(8792, root))
            self.assertTrue(dashboard_launcher._is_any_ooda_dashboard(8792, root))
        with mock.patch.object(dashboard_launcher, "_dashboard_body", return_value=previous):
            self.assertFalse(dashboard_launcher._is_ooda_dashboard(8792, root))
            self.assertTrue(dashboard_launcher._is_any_ooda_dashboard(8792, root))


if __name__ == "__main__":
    unittest.main()
