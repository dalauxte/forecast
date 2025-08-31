from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from typing import Optional

import yaml

from .config import Config, Settings, CapacityConfig, CalendarConfig, SicknessConfig, Project
from .report import create_html_report


def _config_from_dict(data: dict) -> Config:
    settings = Settings.from_dict(data.get("settings") or {})
    capacity = CapacityConfig.from_dict(data.get("capacity") or {})
    calendar = CalendarConfig.from_dict(data.get("calendar") or {})
    sickness = SicknessConfig.from_dict(data.get("sickness") or {})
    projects = [Project.from_dict(x) for x in (data.get("projects") or [])]
    if not projects:
        raise ValueError("Mindestens ein Projekt muss in projects definiert sein")
    return Config(settings=settings, capacity=capacity, calendar=calendar, sickness=sickness, projects=projects)


INDEX_HTML = """<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Forecast – Live</title>
  <style>
    html, body { height: 100%; margin: 0; font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
    .wrap { display: grid; grid-template-columns: 1fr 1fr; height: 100%; }
    .left { padding: 12px; border-right: 1px solid #ddd; display: flex; flex-direction: column; }
    .right { height: 100%; }
    textarea { flex: 1; width: 100%; resize: none; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; }
    .bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
    button { padding: 6px 10px; }
    iframe { width: 100%; height: 100%; border: 0; }
    .err { color: #b00020; font-size: 12px; white-space: pre-wrap; }
  </style>
  <script>
    let timer = null;
    async function renderNow() {
      const ta = document.getElementById('yaml');
      const out = document.getElementById('out');
      const err = document.getElementById('err');
      err.textContent = '';
      try {
        const res = await fetch('/render', { method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: ta.value });
        const text = await res.text();
        if (res.ok) {
          out.srcdoc = text;
        } else {
          err.textContent = text;
        }
      } catch (e) {
        err.textContent = String(e);
      }
    }
    function onInput() {
      if (timer) clearTimeout(timer);
      timer = setTimeout(renderNow, 400);
    }
    window.addEventListener('load', () => {
      document.getElementById('yaml').addEventListener('input', onInput);
      document.getElementById('btn').addEventListener('click', renderNow);
      renderNow();
    });
  </script>
</head>
<body>
  <div class="wrap">
    <div class="left">
      <div class="bar">
        <strong>YAML-Konfiguration</strong>
        <button id="btn">Neu rendern</button>
      </div>
      <textarea id="yaml">{YAML}</textarea>
      <div id="err" class="err"></div>
    </div>
    <div class="right">
      <iframe id="out"></iframe>
    </div>
  </div>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def _send(self, code: int, body: str, content_type: str = "text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def do_GET(self):
        if self.path == "/":
            # try to preload config/config.yml
            preload = ""
            try:
                cfg_path = os.path.join("config", "config.yml")
                if os.path.exists(cfg_path):
                    with open(cfg_path, "r", encoding="utf-8") as f:
                        preload = f.read()
            except Exception:
                preload = ""
            page = INDEX_HTML.replace("{YAML}", preload)
            return self._send(200, page)
        return self._send(404, "Not found", "text/plain; charset=utf-8")

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/render":
            try:
                length = int(self.headers.get("Content-Length", "0"))
                raw = self.rfile.read(length).decode("utf-8") if length > 0 else ""
                data = yaml.safe_load(raw) or {}
                cfg = _config_from_dict(data)
                html = create_html_report(cfg)
                return self._send(200, html)
            except Exception as e:
                return self._send(400, f"Fehler beim Rendern: {e}", "text/plain; charset=utf-8")
        return self._send(404, "Not found", "text/plain; charset=utf-8")


def serve(host: str = "127.0.0.1", port: int = 8765):
    httpd = HTTPServer((host, port), Handler)
    print(f"Live-Server läuft auf http://{host}:{port} — STRG+C zum Beenden")
    httpd.serve_forever()


def main(argv: list[str] | None = None) -> int:
    host = os.environ.get("FORECAST_HOST", "127.0.0.1")
    port = int(os.environ.get("FORECAST_PORT", "8765"))
    serve(host, port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

