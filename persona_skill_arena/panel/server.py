#!/usr/bin/env python3
"""
panel/server.py — 本地 HTTP 服务器，把 dashboard.html 变成可交互圆桌

启动：
    python3 panel/server.py              # 默认 http://localhost:8888
    python3 panel/server.py --port 9000

接口：
    GET  /                 → 吐 dashboard.html
    GET  /api/skills       → 列出已安装的 skill
    POST /api/ask          → SSE 流式返回每个人格的回答
    POST /api/synth        → 一次性返回综合总结

POST /api/ask 请求体:
    { "question": "...", "skills": ["fengge", "munger"]|null, "model": "sonnet", "synth": true }

SSE 事件类型:
    start      { total, skills }
    answer     { skill, answer, error, duration_s }
    synth_start {}
    synth      { text }
    done       {}
"""
from __future__ import annotations

import argparse
import json
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
ARENA = HERE.parent
sys.path.insert(0, str(HERE))

# Reuse everything from ask.py
from ask import (  # noqa: E402
    discover_skills, ask_one, synthesize,
)

DASHBOARD = ARENA / "results" / "dashboard.html"


class Handler(BaseHTTPRequestHandler):

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------
    def _send(self, status: int, content_type: str, body: bytes,
              extra_headers: dict | None = None):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj, status: int = 200):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self._send(status, "application/json; charset=utf-8", body)

    def _write_sse(self, event: str, data: dict) -> bool:
        msg = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        try:
            self.wfile.write(msg.encode("utf-8"))
            self.wfile.flush()
            return True
        except (BrokenPipeError, ConnectionResetError):
            return False

    def log_message(self, fmt, *args):
        # Quieter logs
        sys.stderr.write(f"  [{self.log_date_time_string()}] {fmt % args}\n")

    # ------------------------------------------------------------------
    # GET
    # ------------------------------------------------------------------
    def do_GET(self):
        path = urlparse(self.path).path

        if path in ("/", "/index.html", "/dashboard.html"):
            if not DASHBOARD.exists():
                self._send_json({"error": "dashboard.html not found — run build_dashboard.py first"}, 500)
                return
            body = DASHBOARD.read_bytes()
            self._send(200, "text/html; charset=utf-8", body)
            return

        if path == "/api/skills":
            skills = discover_skills()
            data = [{"name": s.name, "size": s.skill_md_size} for s in skills]
            self._send_json(data)
            return

        if path == "/api/health":
            self._send_json({"ok": True, "skills_found": len(discover_skills())})
            return

        self._send_json({"error": f"not found: {path}"}, 404)

    # ------------------------------------------------------------------
    # POST
    # ------------------------------------------------------------------
    def do_POST(self):
        path = urlparse(self.path).path

        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length > 0 else b""
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            self._send_json({"error": "invalid json"}, 400)
            return

        if path == "/api/ask":
            self._handle_ask(body)
            return

        if path == "/api/synth":
            self._handle_synth(body)
            return

        self._send_json({"error": f"not found: {path}"}, 404)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    # ------------------------------------------------------------------
    # /api/ask (SSE)
    # ------------------------------------------------------------------
    def _handle_ask(self, body: dict):
        question = (body.get("question") or "").strip()
        if not question:
            self._send_json({"error": "empty question"}, 400)
            return

        requested = body.get("skills")  # list or None
        model = body.get("model") or "claude-sonnet-4-6"
        do_synth = bool(body.get("synth", False))
        workers = int(body.get("workers", 6))
        timeout = int(body.get("timeout", 180))

        all_skills = discover_skills()
        if requested:
            wanted = set(requested)
            skills = [s for s in all_skills if s.name in wanted]
        else:
            skills = all_skills

        if not skills:
            self._send_json({"error": "no matching skills"}, 400)
            return

        # Start SSE stream
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        if not self._write_sse("start", {
            "total": len(skills),
            "skills": [s.name for s in skills],
            "question": question,
            "model": model,
        }):
            return

        answers = []
        try:
            with ThreadPoolExecutor(max_workers=workers) as pool:
                futures = {
                    pool.submit(ask_one, s, question, model, timeout): s
                    for s in skills
                }
                for fut in as_completed(futures):
                    ans = fut.result()
                    answers.append(ans)
                    payload = {
                        "skill": ans.skill,
                        "answer": ans.answer,
                        "error": ans.error,
                        "duration_s": round(ans.duration_s or 0.0, 1),
                    }
                    if not self._write_sse("answer", payload):
                        return
        except Exception as e:
            self._write_sse("error", {"message": str(e)})
            return

        if do_synth and any(a.answer for a in answers):
            self._write_sse("synth_start", {})
            try:
                synth_text = synthesize(question, answers, model, timeout)
                self._write_sse("synth", {"text": synth_text or ""})
            except Exception as e:
                self._write_sse("synth", {"text": f"[synth failed: {e}]"})

        self._write_sse("done", {"count": len(answers)})

    # ------------------------------------------------------------------
    # /api/synth (one-shot)
    # ------------------------------------------------------------------
    def _handle_synth(self, body: dict):
        # not used by the dashboard currently; kept for completeness
        self._send_json({"error": "use /api/ask with synth=true instead"}, 400)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8888)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), Handler)
    print(f"\n  🎭 SBTI Panel Server")
    print(f"  ──────────────────────────────────")
    print(f"  Open:    http://{args.host}:{args.port}/")
    print(f"  Health:  http://{args.host}:{args.port}/api/health")
    print(f"  Skills:  {len(discover_skills())} installed")
    print(f"  (Ctrl-C to stop)\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  bye")


if __name__ == "__main__":
    main()
