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
            port, reuse = dashboard_launcher._select_port(8791, root)

        self.assertEqual(port, 8791)
        self.assertTrue(reuse)
        port_open.assert_not_called()

    def test_skips_foreign_service_on_preferred_port(self):
        root = Path("/tmp/repos")

        def is_ooda(port, _root):
            return False

        def port_open(port):
            return port == 8791

        with mock.patch.object(dashboard_launcher, "_is_ooda_dashboard", side_effect=is_ooda), mock.patch.object(
            dashboard_launcher, "_port_open", side_effect=port_open
        ):
            port, reuse = dashboard_launcher._select_port(8791, root)

        self.assertEqual(port, 8792)
        self.assertFalse(reuse)

    def test_finds_existing_ooda_dashboard_after_foreign_port(self):
        root = Path("/tmp/repos")

        def is_ooda(port, _root):
            return port == 8792

        def port_open(port):
            return port == 8791

        with mock.patch.object(dashboard_launcher, "_is_ooda_dashboard", side_effect=is_ooda), mock.patch.object(
            dashboard_launcher, "_port_open", side_effect=port_open
        ):
            port, reuse = dashboard_launcher._select_port(8791, root)

        self.assertEqual(port, 8792)
        self.assertTrue(reuse)


if __name__ == "__main__":
    unittest.main()
