"""Mock Ollama server for DS_101b/DS_101c fallback testing.

Responds with invalid JSON on the first N requests to /api/chat,
then returns valid JSON arrays matching the issues in the batch.
Listens on a separate port (default 11500) so the real Ollama
on 11434 is not affected.

DS_101c fix: extract element count from prompt instruction
("exactly N elements") so the EXAMPLE block line numbers are not
included in the returned array.
"""

import argparse
import json
import re
import sys
import threading
import time
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler

# --- Global state ---
counter = 0
lock = threading.Lock()
fail_count = 1
fail_content = "not a valid json at all"
default_count = 10


def _increment_and_get():
    """Atomically increment and return the request counter."""
    global counter
    with lock:
        counter += 1
        return counter


def _extract_count(content: str) -> int | None:
    """Find the explicit element count from prompt instruction.

    Looks for 'exactly N elements' (e.g. "Return ONLY a JSON array
    with exactly 10 elements"). Returns int or None if not found.
    """
    m = re.search(r'exactly\s+(\d+)\s+elements', content)
    if m:
        return int(m.group(1))
    return None


def _extract_lines(content: str) -> list[int]:
    """Extract line numbers from the ISSUES: section only.

    Scans text AFTER "ISSUES:" (case-sensitive) so the EXAMPLE block
    at the top of the prompt (which contains e.g. "line 32,") is
    ignored. If "ISSUES:" is not found, scans the whole content.
    """
    section = content
    idx = content.find("ISSUES:")
    if idx != -1:
        section = content[idx + len("ISSUES:"):]
    matches = re.findall(r'\bline\s+(\d+)\s*,', section)
    return [int(m) for m in matches]


def _make_fix_array(n: int, lines: list[int]) -> list[dict]:
    """Build a valid JSON fix array of EXACTLY n elements.

    - If lines has more than n entries, trim to n.
    - If lines has fewer than n, pad with last+1, last+2, ...
    - If lines is empty, use range(1, n+1).
    """
    if not lines:
        lines = list(range(1, n + 1))
    if len(lines) > n:
        lines = lines[:n]
    while len(lines) < n:
        lines.append(lines[-1] + 1 if lines else 1)
    return [
        {
            "line": ln,
            "after": "mock fixed line",
            "reason": "mock fallback test",
            "confidence": 0.95,
        }
        for ln in lines
    ]


class MockOllamaHandler(BaseHTTPRequestHandler):
    """HTTP handler mimicking the Ollama REST API."""

    def log_message(self, format, *args):
        """Suppress default stderr logging; we use print instead."""
        pass

    def _send_json(self, data: dict | list) -> None:
        body_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body_bytes)))
        self.end_headers()
        self.wfile.write(body_bytes)

    def do_GET(self):
        if self.path == "/api/tags":
            response = {
                "models": [
                    {"name": "qwen2.5-coder:7b", "model": "qwen2.5-coder:7b"}
                ]
            }
            self._send_json(response)
            print(f"req#? GET /api/tags → ok", flush=True)
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_response(404)
            self.end_headers()
            return

        req_num = _increment_and_get()

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length) if content_length else b"{}"

        # Parse request to extract user content for line detection
        try:
            req_data = json.loads(raw_body.decode("utf-8"))
            messages = req_data.get("messages", [])
            user_content = ""
            for msg in messages:
                if msg.get("role") == "user":
                    user_content = msg.get("content", "")
                    break
        except (json.JSONDecodeError, UnicodeDecodeError):
            user_content = ""

        # Decide response based on counter
        if req_num <= fail_count:
            content_str = fail_content
            status_label = "invalid"
        else:
            # DS_101c: try explicit count from "exactly N elements" first
            n = _extract_count(user_content)
            if n is None:
                # Fallback: use lines from ISSUES: section
                lines = _extract_lines(user_content)
                n = len(lines) if lines else default_count
            else:
                lines = _extract_lines(user_content)
            fix_array = _make_fix_array(n, lines)
            content_str = json.dumps(fix_array, ensure_ascii=False)
            status_label = "valid"

        # Build Ollama-style response
        response = {
            "model": "qwen2.5-coder:7b",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "message": {
                "role": "assistant",
                "content": content_str,
            },
            "done": True,
        }

        self._send_json(response)
        print(f"req#{req_num} POST /api/chat → {status_label}", flush=True)


def main():
    global fail_count, fail_content, default_count

    parser = argparse.ArgumentParser(description="Mock Ollama server for fallback testing")
    parser.add_argument("--port", type=int, default=11500, help="Port to listen on")
    parser.add_argument("--host", type=str, default="localhost", help="Host to bind")
    parser.add_argument("--fail-first", action="store_true", default=True,
                        help="Make first request(s) invalid (default True)")
    parser.add_argument("--fail-count", type=int, default=1,
                        help="Number of first requests to break")
    parser.add_argument("--fail-content", type=str, default="not a valid json at all",
                        help="Content returned for invalid responses")
    parser.add_argument("--default-count", type=int, default=10,
                        help="Number of elements if no line pattern found")
    args = parser.parse_args()

    fail_count = args.fail_count if args.fail_first else 0
    fail_content = args.fail_content
    default_count = args.default_count

    try:
        server = HTTPServer((args.host, args.port), MockOllamaHandler)
    except OSError as exc:
        print(f"port {args.port} busy: {exc}")
        sys.exit(1)

    print(f"mock-ollama listening on http://{args.host}:{args.port}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("mock-ollama stopped", flush=True)
        server.server_close()


if __name__ == "__main__":
    main()
