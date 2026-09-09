from __future__ import annotations

import html
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path


DEFAULT_PORT = 8792
PORT_SEARCH_SPAN = 20
CURRENT_UI_MARKERS = (
    "project-sidebar",
    "efficiency-chart",
    "attention-strip",
    "domain-orientation-grid",
)


def _port_open(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.2)
        return sock.connect_ex(("127.0.0.1", port)) == 0


def _dashboard_body(port: int) -> str | None:
    url = f"http://127.0.0.1:{port}/"
    try:
        with urllib.request.urlopen(url, timeout=0.4) as response:
            return response.read(65536).decode("utf-8", errors="replace")
    except (OSError, urllib.error.URLError, ValueError):
        return None


def _is_any_ooda_dashboard(port: int, root: Path) -> bool:
    body = _dashboard_body(port)
    if body is None:
        return False
    return (
        "<title>OODA Control Room</title>" in body
        and html.escape(str(root)) in body
    )


def _is_ooda_dashboard(port: int, root: Path) -> bool:
    """Return True only for a dashboard from the current Control Room UI generation.

    A browser refresh cannot replace an already-running Python process after OODA is
    upgraded. Reusing any page with the right title/root therefore served stale UI
    indefinitely. The stable structural markers below let the launcher distinguish
    the current domain-first Control Room from an older process without killing
    arbitrary local processes.
    """
    body = _dashboard_body(port)
    if body is None:
        return False
    return (
        "<title>OODA Control Room</title>" in body
        and html.escape(str(root)) in body
        and all(marker in body for marker in CURRENT_UI_MARKERS)
    )


def _select_port(preferred: int, root: Path) -> tuple[int, bool]:
    """Return (port, reuse_existing_current_ooda_dashboard)."""
    for port in range(preferred, preferred + PORT_SEARCH_SPAN):
        if _is_ooda_dashboard(port, root):
            return port, True
        if not _port_open(port):
            return port, False
    raise RuntimeError(
        f"No free OODA dashboard port found in {preferred}-{preferred + PORT_SEARCH_SPAN - 1}"
    )


def launch() -> int:
    root = Path(
        os.environ.get("OODA_PROJECTS_ROOT", str(Path.home() / "repos"))
    ).expanduser()
    preferred = int(os.environ.get("OODA_DASHBOARD_PORT", str(DEFAULT_PORT)))

    stale_preferred = _is_any_ooda_dashboard(preferred, root) and not _is_ooda_dashboard(preferred, root)

    try:
        port, reuse = _select_port(preferred, root)
    except (ValueError, RuntimeError) as exc:
        print(f"OODA dashboard: {exc}", file=sys.stderr)
        return 2

    url = f"http://127.0.0.1:{port}/"

    if port != preferred:
        if stale_preferred:
            print(
                f"OODA dashboard: stale pre-upgrade Control Room is still running on port {preferred}; "
                f"starting the current UI on {port}. The old process is left untouched."
            )
        else:
            print(
                f"OODA dashboard: port {preferred} is in use by another service; using {port} instead."
            )

    if not reuse:
        log_dir = Path.home() / ".ooda"
        log_dir.mkdir(parents=True, exist_ok=True)
        log = (log_dir / "dashboard.log").open("a", encoding="utf-8")
        env = os.environ.copy()
        env["OODA_DASHBOARD_PORT"] = str(port)
        env["OODA_PROJECTS_ROOT"] = str(root)
        subprocess.Popen(
            [sys.executable, "-m", "ooda.domain_control_room", "--serve"],
            stdout=log,
            stderr=log,
            start_new_session=True,
            close_fds=True,
            env=env,
        )
        for _ in range(30):
            if _is_ooda_dashboard(port, root):
                break
            time.sleep(0.1)
        else:
            print(
                f"OODA dashboard failed to start; see {log_dir / 'dashboard.log'}",
                file=sys.stderr,
            )
            return 2

    print(url)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    return 0
