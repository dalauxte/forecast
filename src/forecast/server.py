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


INDEX_HTML = r"""<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="utf-8">
  <title>Forecast – Live</title>
  <style>
    html, body { height: 100%; margin: 0; font-family: -apple-system, Segoe UI, Roboto, Arial, sans-serif; }
    :root { --left: 35%; }
    .wrap { display: flex; height: 100%; }
    .left { width: var(--left); min-width: 240px; padding: 12px; border-right: 1px solid #ddd; display: flex; flex-direction: column; box-sizing: border-box; }
    .drag { width: 6px; cursor: col-resize; background: #f5f5f5; border-right: 1px solid #e0e0e0; border-left: 1px solid #e0e0e0; }
    .right { flex: 1; height: 100%; }
    textarea { flex: 1; width: 100%; resize: none; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; box-sizing: border-box; }
    .bar { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; gap: 8px; }
    .bar .actions { display: flex; gap: 6px; }
    button { padding: 6px 10px; }
    .editor { position: relative; flex: 1; }
    .editor textarea {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; line-height: 1.4;
      width: 100%; height: 100%; box-sizing: border-box; margin: 0;
      padding: 10px; border: 1px solid #e0e0e0; border-radius: 4px;
      background: #fff; color: #111; caret-color: #111; resize: none;
    }
    iframe { width: 100%; height: 100%; border: 0; }
    .err { color: #b00020; font-size: 12px; white-space: pre-wrap; }
  </style>
  <script>
    let timer = null;
    function clampSplit(p) { return Math.max(20, Math.min(80, p)); }
    function setSplit(pct) {
      const root = document.documentElement;
      const val = clampSplit(pct).toFixed(1) + '%';
      root.style.setProperty('--left', val);
      localStorage.setItem('splitLeft', val);
    }
    // No syntax highlighting to ensure broad compatibility
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
      const root = document.documentElement;
      const saved = localStorage.getItem('splitLeft');
      root.style.setProperty('--left', saved || '35%');

      const ta = document.getElementById('yaml');
      ta.addEventListener('input', onInput);
      document.getElementById('btn').addEventListener('click', renderNow);
      const reset = document.getElementById('reset'); if (reset) reset.addEventListener('click', () => setSplit(35));
      // Highlighting toggle
      const leftPane = document.querySelector('.left');
      const hlToggle = document.getElementById('toggle-hl');
      const savedHL = localStorage.getItem('hlEnabled');
      if (savedHL === '1') { leftPane.classList.add('hl-on'); }
      if (hlToggle) {
        hlToggle.checked = leftPane.classList.contains('hl-on');
        hlToggle.addEventListener('change', () => {
          if (hlToggle.checked) {
            leftPane.classList.add('hl-on');
            localStorage.setItem('hlEnabled', '1');
            syncHighlight();
          } else {
            leftPane.classList.remove('hl-on');
            localStorage.setItem('hlEnabled', '0');
          }
        });
      }

      // Drag to resize
      const drag = document.getElementById('drag');
      const wrap = document.getElementById('wrap');
      let dragging = false;
      drag.addEventListener('mousedown', (e) => { dragging = true; e.preventDefault(); });
      window.addEventListener('mouseup', () => { dragging = false; });
      window.addEventListener('mousemove', (e) => {
        if (!dragging) return;
        const rect = wrap.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const pct = (x / rect.width) * 100;
        setSplit(pct);
      });
      // Keyboard resize: Alt + ArrowLeft/Right
      window.addEventListener('keydown', (e) => {
        if (!e.altKey) return;
        const cur = parseFloat(getComputedStyle(root).getPropertyValue('--left')) || 35;
        if (e.key === 'ArrowLeft') { setSplit(cur - 1); e.preventDefault(); }
        if (e.key === 'ArrowRight') { setSplit(cur + 1); e.preventDefault(); }
      });

      renderNow();
    });
  </script>
</head>
<body>
  <div id="wrap" class="wrap">
    <div class="left">
      <div class="bar">
        <strong>YAML-Konfiguration</strong>
        <span class="actions">
          <label style="font-weight:normal; font-size:12px; display:inline-flex; align-items:center; gap:4px;"><input type="checkbox" id="toggle-hl"> Highlighting</label>
          <button id="btn">Neu rendern</button>
          <button id="reset" title="Reset auf 35%">Reset</button>
        </span>
      </div>
      <div class="editor">
        <textarea id="yaml">{YAML}</textarea>
      </div>
      <div id="err" class="err"></div>
    </div>
    <div id="drag" class="drag" title="Ziehen zum Anpassen"></div>
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
