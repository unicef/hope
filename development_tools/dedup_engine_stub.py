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
]

FINDINGS_RESPONSES: dict[str, tuple[int, dict]] = {
    "cw-stub-rdi-a": (
        200,
        {
            "results": [
                {
                    "first": {"reference_pk": "cw-ind-a-0"},
                    "second": {"reference_pk": "cw-ind-a-1"},
                    "score": 0.95,
                    "status_code": "200",
                },
                {
                    "first": {"reference_pk": "cw-ind-a-1"},
                    "second": {"reference_pk": "cw-ind-a-2"},
                    "score": 0.78,
                    "status_code": "200",
                },
                {
                    "first": {"reference_pk": "cw-ind-a-2"},
                    "second": {"reference_pk": "cw-ind-a-3"},
                    "score": 0.0,
                    "status_code": "418",
                },
            ],
            "next": None,
        },
    ),
    "cw-stub-rdi-b": (200, {"results": [], "next": None}),
    "cw-stub-rdi-c": (
        200,
        {
            "results": [
                {
                    "first": {"reference_pk": "cw-ind-c-0"},
                    "second": {"reference_pk": "cw-ind-c-1"},
                    "score": 0.92,
                    "status_code": "200",
                },
                {
                    "first": {"reference_pk": "cw-ind-c-1"},
                    "second": {"reference_pk": "cw-ind-c-2"},
                    "score": 0.81,
                    "status_code": "200",
                },
                {
                    "first": {"reference_pk": "cw-ind-c-2"},
                    "second": {"reference_pk": "cw-ind-c-3"},
                    "score": 0.0,
                    "status_code": "412",
                },
            ],
            "next": "http://127.0.0.1:8889/deduplication_set_groups/cw-stub-rdi-c/findings/?page=2",
        },
    ),
    "cw-stub-rdi-c?page=2": (
        200,
        {
            "results": [
                {
                    "first": {"reference_pk": "cw-ind-c-3"},
                    "second": {"reference_pk": "cw-ind-c-4"},
                    "score": 0.65,
                    "status_code": "200",
                },
                {
                    "first": {"reference_pk": "cw-ind-c-4"},
                    "second": {"reference_pk": "cw-ind-c-5"},
                    "score": 0.0,
                    "status_code": "418",
                },
            ],
            "next": None,
        },
    ),
}

_approved: set[str] = set()

_FINDINGS_RE = re.compile(r"^/deduplication_set_groups/([^/]+)/findings/$")
_APPROVE_RE = re.compile(r"^/deduplication_set_groups/([^/]+)/approve/$")


def _findings_response(reference_id: str, query: str) -> tuple[int, object]:
    page = ""
    for part in query.split("&"):
        if part.startswith("page="):
            page = part.split("=", 1)[1]
            break
    key = f"{reference_id}?page={page}" if page else reference_id
    if key in FINDINGS_RESPONSES:
        return FINDINGS_RESPONSES[key]
    return 404, {"detail": "Group not found"}


def _approve_response(reference_id: str) -> tuple[int, object]:
    if reference_id in _approved:
        return 409, {"detail": "Group already approved"}
    _approved.add(reference_id)
    return 200, {}


class _Handler(BaseHTTPRequestHandler):
    server_version = "DedupEngineStub/1.0"

    def _dispatch(self, method: str) -> None:
        path, _, query = self.path.partition("?")

        if method == "GET":
            m = _FINDINGS_RE.match(path)
            if m:
                status, body = _findings_response(m.group(1), query)
                self._respond(status, body)
                return
        if method == "POST":
            m = _APPROVE_RE.match(path)
            if m:
                status, body = _approve_response(m.group(1))
                self._respond(status, body)
                return

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
