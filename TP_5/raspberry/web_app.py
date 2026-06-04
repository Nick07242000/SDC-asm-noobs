#!/usr/bin/env python3

import http.server
import json
import threading
import time
 
DEVICE_PATH = "/dev/asmn_driver"
PORT = 8080
 
history = []
history_lock = threading.Lock()
 
def sampler():
    while True:
        try:
            with open(DEVICE_PATH, "r") as f:
                data = f.read().strip()
            parts = data.split(":")
            if len(parts) == 2:
                t, v = int(parts[0].strip()), int(parts[1].strip())
                with history_lock:
                    if not history or history[-1]["t"] != t:
                        history.append({"t": t, "v": v})
                        history[:] = history[-60:]
        except Exception as e:
            print(f"[sampler] {e}")
        time.sleep(0.5)
 
HTML = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>ASMN Driver</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    body { font-family: Arial, sans-serif; background: #1e1e2e; color: #cdd6f4;
           display: flex; flex-direction: column; align-items: center; padding: 2rem; }
    canvas { background: #313244; border-radius: 8px; }
    button { margin: .5rem; padding: .5rem 1.5rem; border: none;
             border-radius: 6px; cursor: pointer; font-size: 1rem; }
    #btn0 { background: #89b4fa; color: #1e1e2e; }
    #btn1 { background: #f38ba8; color: #1e1e2e; }
  </style>
</head>
<body>
  <h2>ASMN Driver — Visualización en tiempo real</h2>
  <div>
    <button id="btn0" onclick="setChannel(0)">Señal 1 (Lineal)</button>
    <button id="btn1" onclick="setChannel(1)">Señal 2 (Aleatoria)</button>
  </div>
  <canvas id="chart" width="700" height="350"></canvas>
  <script>
    const ctx = document.getElementById('chart').getContext('2d');
    const chart = new Chart(ctx, {
      type: 'line',
      data: { labels: [], datasets: [{ label: 'Señal', data: [],
              borderColor: '#89b4fa', tension: 0.3, pointRadius: 4 }] },
      options: { animation: false, scales: {
        x: { title: { display: true, text: 'Tiempo (s)' } },
        y: { title: { display: true, text: 'Valor' }, min: 0, max: 105 } } }
    });
    function setChannel(ch) {
      fetch('/channel', { method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ channel: ch }) });
      chart.data.labels = [];
      chart.data.datasets[0].data = [];
      chart.data.datasets[0].borderColor = ch === 0 ? '#89b4fa' : '#f38ba8';
      chart.data.datasets[0].label = ch === 0 ? 'Señal 1 (Lineal)' : 'Señal 2 (Aleatoria)';
      chart.update();
    }
    setInterval(async () => {
      const pts = await (await fetch('/data')).json();
      chart.data.labels = pts.map(p => p.t);
      chart.data.datasets[0].data = pts.map(p => p.v);
      chart.update();
    }, 500);
  </script>
</body>
</html>"""
 
class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        if self.path == "/":
            body = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers(); self.wfile.write(body)
        elif self.path == "/data":
            with history_lock:
                payload = json.dumps(list(history)).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers(); self.wfile.write(payload)
        else:
            self.send_response(404); self.end_headers()
    def do_POST(self):
        if self.path == "/channel":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))
            ch = int(body.get("channel", 0))
            try:
                with open(DEVICE_PATH, "w") as f:
                    f.write(str(ch))
                with history_lock:
                    history.clear()
            except Exception as e:
                print(f"[channel] {e}")
            self.send_response(200); self.end_headers()
 
if __name__ == "__main__":
    threading.Thread(target=sampler, daemon=True).start()
    print(f"Servidor en http://0.0.0.0:{PORT}")
    http.server.HTTPServer(("", PORT), Handler).serve_forever()