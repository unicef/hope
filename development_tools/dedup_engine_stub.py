"""Minimal HTTP stub for the external deduplication engine.

Use during local dev (`make dev`) so the biometric dedup flow completes in the
browser without a real engine behind `DEDUPLICATION_ENGINE_API_URL`.

Usage:
    make dedup-stub
    # then in .env:
    #   DEDUPLICATION_ENGINE_API_URL="http://localhost:8889/"
    #   DEDUPLICATION_ENGINE_API_KEY="test"
    # restart `make serve` after changing .env

Every endpoint HOPE's `DeduplicationEngineAPI` calls returns a deterministic
happy-path response. Requests are logged so you can confirm your click
actually reached the stub.

For E2E tests, use the `dedup_engine_stub` fixture in tests/e2e/conftest.py —
it's in-process and doesn't need this server running.
"""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import re

ROUTES: list[tuple[str, re.Pattern[str], int, object]] = [
    ("POST", re.compile(r"^/deduplication_sets/$"), 200, {}),
    ("GET", re.compile(r"^/deduplication_sets/[^/]+/$"), 200, {"state": "Ready", "error": ""}),
    ("DELETE", re.compile(r"^/deduplication_sets/[^/]+/$"), 200, {}),
    ("POST", re.compile(r"^/deduplication_sets/[^/]+/process/$"), 200, {}),
    ("POST", re.compile(r"^/deduplication_sets/[^/]+/images_bulk/$"), 200, []),
    ("DELETE", re.compile(r"^/deduplication_sets/[^/]+/images_bulk/clear/$"), 200, {}),
    ("GET", re.compile(r"^/deduplication_sets/[^/]+/duplicates/$"), 200, {"results": [], "next": None}),
    ("POST", re.compile(r"^/deduplication_sets/[^/]+/ignored/filenames/$"), 200, {}),
    ("POST", re.compile(r"^/deduplication_sets/[^/]+/approve_or_reject/$"), 200, {}),
    # Ticket 306312: new resource family.
    ("GET", re.compile(r"^/deduplication_set_groups/[^/]+/findings/$"), 200, {"findings": []}),
    ("POST", re.compile(r"^/deduplication_set_groups/[^/]+/approve/$"), 200, {}),
]


class _Handler(BaseHTTPRequestHandler):
    server_version = "DedupEngineStub/1.0"

    def _dispatch(self, method: str) -> None:
        path = self.path.split("?", 1)[0]
        for expected_method, pattern, status, body in ROUTES:
            if expected_method == method and pattern.match(path):
                self._respond(status, body)
                return
        self._respond(404, {"detail": f"No stub route for {method} {path}"})

    def _respond(self, status: int, payload: object) -> None:
        data = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        self._dispatch("GET")

    def do_POST(self) -> None:
        # Drain the body so keep-alive clients aren't left hanging.
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        self._dispatch("POST")

    def do_DELETE(self) -> None:
        self._dispatch("DELETE")


def main() -> None:
    parser = argparse.ArgumentParser(description="Dedup engine HTTP stub")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8889)
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), _Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
