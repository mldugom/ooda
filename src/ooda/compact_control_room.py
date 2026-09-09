from __future__ import annotations

import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List
from urllib.parse import urlparse

from .dashboard import discover_projects
from .domain_control_room import render_html
from .control_room import _read_json


def _current_gate(project: Dict[str, Any]) -> str:
    repo = project.get("repo")
    if isinstance(repo, Path):
        view = _read_json(repo / ".ooda" / "project-view.json")
        if view.get("schema") == "ooda/project-view/v1":
            gate = view.get("human_gate") or view.get("next_gate")
            if gate:
                return str(gate)
    return str(project.get("next_gate") or "No human/next gate recorded")


def _fresh_projects(root: Path) -> List[Dict[str, Any]]:
    projects = discover_projects(root)
    out: List[Dict[str, Any]] = []
    for project in projects:
        item = dict(project)
        item["next_gate"] = _current_gate(project)
        out.append(item)
    return out


class _Handler(BaseHTTPRequestHandler):
    root = Path.home() / "repos"
    refresh_seconds = 15

    def do_GET(self) -> None:
        if urlparse(self.path).path not in {"/", "/index.html"}:
            self.send_error(404)
            return
        body = render_html(_fresh_projects(self.root), self.refresh_seconds, self.root).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def serve() -> None:
    root = Path(os.environ.get("OODA_PROJECTS_ROOT", str(Path.home() / "repos"))).expanduser()
    port = int(os.environ.get("OODA_DASHBOARD_PORT", "8792"))
    refresh = max(0, int(os.environ.get("OODA_DASHBOARD_REFRESH_SECONDS", "15")))
    _Handler.root = root
    _Handler.refresh_seconds = refresh
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    print(f"OODA Control Room serving http://127.0.0.1:{port}/")
    server.serve_forever()


def main() -> None:
    if "--serve" in sys.argv[1:]:
        serve()
        return
    from .dashboard_launcher import launch
    raise SystemExit(launch())


if __name__ == "__main__":
    main()
