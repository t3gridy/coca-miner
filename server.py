#!/usr/bin/env python3
"""Local-only web server for COCA Miner.

Uses only Python's standard library. The GUI is served on 127.0.0.1 and
progress.json is atomically read/written beside this script.
"""
from __future__ import annotations

import json
import mimetypes
import os
import tempfile
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
CONFIG_PATH = ROOT / "config.json"
DEFAULT_CONFIG = {
    "host": "127.0.0.1",
    "port": 8766,
    "open_browser": True,
    "progress_file": "progress.json",
}


def load_config() -> dict:
    """Load local runtime settings, falling back safely to defaults."""
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(
            json.dumps(DEFAULT_CONFIG, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        config = dict(DEFAULT_CONFIG)
    else:
        try:
            config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Cannot read config.json: {exc}") from exc
        if not isinstance(config, dict):
            raise SystemExit("config.json must contain a JSON object")
        config = {**DEFAULT_CONFIG, **config}

    host = str(config.get("host", DEFAULT_CONFIG["host"]))
    if host not in {"127.0.0.1", "localhost"}:
        raise SystemExit('config.json "host" must be "127.0.0.1" or "localhost"')
    try:
        port = int(os.environ.get("COCA_MINER_PORT", config["port"]))
    except (TypeError, ValueError) as exc:
        raise SystemExit('config.json "port" must be an integer') from exc
    if not 1 <= port <= 65535:
        raise SystemExit('config.json "port" must be between 1 and 65535')
    progress_file = str(config.get("progress_file", DEFAULT_CONFIG["progress_file"]))
    if not progress_file or Path(progress_file).name != progress_file or progress_file in {".", ".."}:
        raise SystemExit('config.json "progress_file" must be a filename in the app directory')
    config["host"] = host
    config["port"] = port
    config["open_browser"] = bool(config.get("open_browser", True))
    config["progress_file"] = progress_file
    return config


CONFIG = load_config()
HOST = CONFIG["host"]
PORT = CONFIG["port"]
MAX_PROGRESS_BYTES = 8 * 1024 * 1024
PROGRESS_PATH = ROOT / CONFIG["progress_file"]
STATIC_FILES = {
    "/": ROOT / "index.html",
    "/index.html": ROOT / "index.html",
    "/words.csv": ROOT / "words.csv",
}


class LocalhostHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True


class Handler(BaseHTTPRequestHandler):
    server_version = "COCA-Miner-Local/1.0"

    def log_message(self, fmt: str, *args: object) -> None:
        print("[COCA Miner] " + (fmt % args))

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: object) -> None:
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self._send(status, body, "application/json; charset=utf-8")

    def _valid_host(self) -> bool:
        try:
            parsed = urlsplit("//" + self.headers.get("Host", ""))
            return (
                parsed.hostname in {"localhost", "127.0.0.1"}
                and parsed.port == PORT
            )
        except ValueError:
            return False

    def _valid_origin(self) -> bool:
        origin = self.headers.get("Origin")
        if not origin:
            return True
        try:
            parsed = urlsplit(origin)
            return (
                parsed.scheme == "http"
                and parsed.hostname in {"localhost", "127.0.0.1"}
                and parsed.port == PORT
            )
        except ValueError:
            return False

    def _not_found(self) -> None:
        self._json(404, {"error": "not found"})

    def do_GET(self) -> None:
        if not self._valid_host():
            self._json(421, {"error": "localhost requests only"})
            return

        path = urlsplit(self.path).path
        if path == "/api/health":
            self._json(200, {"ok": True, "storage": "progress.json"})
            return

        if path == "/api/progress":
            if not PROGRESS_PATH.exists():
                self._json(200, {"exists": False})
                return
            try:
                data = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    raise ValueError("progress root must be a JSON object")
            except (OSError, json.JSONDecodeError, ValueError):
                self._json(500, {"error": "progress.json is invalid or unreadable"})
                return
            self._json(200, data)
            return

        file_path = STATIC_FILES.get(path)
        if file_path is None or not file_path.is_file():
            self._not_found()
            return
        try:
            body = file_path.read_bytes()
        except OSError:
            self._json(500, {"error": "could not read static file"})
            return
        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        if content_type.startswith("text/") or content_type in {"application/javascript", "application/json"}:
            content_type += "; charset=utf-8"
        self._send(200, body, content_type)

    def do_PUT(self) -> None:
        self._write_progress()

    def do_POST(self) -> None:
        self._write_progress()

    def _write_progress(self) -> None:
        if not self._valid_host() or not self._valid_origin():
            self._json(403, {"error": "localhost origin required"})
            return
        if urlsplit(self.path).path != "/api/progress":
            self._not_found()
            return
        content_type = self.headers.get("Content-Type", "")
        if not content_type.lower().startswith("application/json"):
            self._json(415, {"error": "application/json required"})
            return
        try:
            length = int(self.headers.get("Content-Length", ""))
        except ValueError:
            self._json(411, {"error": "Content-Length required"})
            return
        if length < 0:
            self._json(400, {"error": "invalid Content-Length"})
            return
        if length > MAX_PROGRESS_BYTES:
            self._json(413, {"error": "progress JSON is too large"})
            return

        try:
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            if not isinstance(data, dict):
                raise ValueError("JSON root must be an object")
            for key in ("decisions", "ankiAdded", "cols", "settings"):
                if key in data and not isinstance(data[key], dict):
                    raise ValueError(f"{key} must be an object")
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self._json(400, {"error": f"invalid progress JSON: {exc}"})
            return

        encoded = (json.dumps(data, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        temp_path: str | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".progress-", suffix=".tmp",
                dir=ROOT, delete=False
            ) as temp_file:
                temp_path = temp_file.name
                temp_file.write(encoded)
                temp_file.flush()
                os.fsync(temp_file.fileno())
            os.replace(temp_path, PROGRESS_PATH)
        except OSError:
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    pass
            self._json(500, {"error": "could not save progress.json"})
            return
        self._json(200, {"ok": True})


def main() -> None:
    if not 1 <= PORT <= 65535:
        raise SystemExit("COCA_MINER_PORT must be between 1 and 65535")
    server = LocalhostHTTPServer((HOST, PORT), Handler)
    url = f"http://127.0.0.1:{PORT}/"
    print(f"COCA Miner is running at {url}")
    print(f"Progress file: {PROGRESS_PATH}")
    print(f"Settings file: {CONFIG_PATH}")
    print("Only this computer can connect. Press Ctrl+C to stop.")
    if CONFIG["open_browser"] and os.environ.get("COCA_MINER_NO_BROWSER") != "1":
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping COCA Miner...")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
