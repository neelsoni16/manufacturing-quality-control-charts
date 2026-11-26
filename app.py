import json
import sqlite3
import subprocess
import urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "quality_control.db"
CHART_PATH = BASE_DIR / "reports" / "control_charts.png"


def get_dashboard_data():
    if not DB_PATH.exists():
        subprocess.run(["py", "-3.12", str(BASE_DIR / "src" / "main.py")], check=True)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    total_batches = cur.execute("SELECT COUNT(*) FROM Sample_Batches").fetchone()[0]
    limits = cur.execute(
        "SELECT center_line, ucl, lcl FROM Control_Limits WHERE chart_type='X-bar'"
    ).fetchone()
    x_dbar, x_ucl, x_lcl = limits if limits else (10.0, 10.067, 9.933)

    xbar_alerts = cur.execute(
        "SELECT COUNT(*) FROM Control_Alerts WHERE chart_type='X-bar'"
    ).fetchone()[0]
    cusum_alerts = cur.execute(
        "SELECT COUNT(*) FROM Control_Alerts WHERE chart_type='CUSUM'"
    ).fetchone()[0]

    alerts = cur.execute(
        "SELECT alert_id, batch_id, chart_type, reason FROM Control_Alerts "
        "WHERE batch_id <= 135 OR batch_id > 200 ORDER BY alert_id ASC"
    ).fetchall()

    batches = cur.execute(
        "SELECT batch_id, batch_mean, batch_range, is_baseline "
        "FROM Sample_Batches ORDER BY batch_id ASC"
    ).fetchall()

    conn.close()
    return {
        "total_batches": total_batches,
        "x_dbar": x_dbar,
        "x_ucl": x_ucl,
        "x_lcl": x_lcl,
        "xbar_alerts": xbar_alerts,
        "cusum_alerts": cusum_alerts,
        "alerts": alerts,
        "batches": batches,
    }


def render_page(data):
    alert_rows = "\n".join(
        f"<tr>"
        f"<td>#{a[0]}</td>"
        f"<td>Batch {a[1]}</td>"
        f"<td><span class='badge {'badge-xbar' if a[2] == 'X-bar' else 'badge-cusum'}'>{a[2]}</span></td>"
        f"<td>{a[3]}</td>"
        f"</tr>"
        for a in data["alerts"]
    )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Project 9 | Manufacturing Quality Control Portal</title>
  <style>
    * {{ box-sizing: border-box; }}
    body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f3f4f6; color: #1f2937; margin: 0; padding: 24px; }}
    .container {{ max-width: 1120px; margin: auto; }}
    .header {{ background: #1e3a8a; color: white; padding: 22px 28px; border-radius: 10px; margin-bottom: 20px; }}
    .header h1 {{ margin: 0 0 6px; font-size: 24px; }}
    .header p {{ margin: 0; opacity: 0.9; font-size: 14px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 20px; }}
    .card {{ background: white; padding: 18px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); }}
    .card h3 {{ margin: 0 0 8px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; color: #6b7280; }}
    .card .val {{ font-size: 24px; font-weight: 700; color: #111827; }}
    .card .alert {{ color: #dc2626; }}
    .panel {{ background: white; padding: 22px; border-radius: 10px; box-shadow: 0 2px 6px rgba(0,0,0,0.06); margin-bottom: 20px; }}
    .panel h2 {{ margin-top: 0; font-size: 18px; color: #1e3a8a; }}
    img {{ max-width: 100%; border-radius: 6px; border: 1px solid #e5e7eb; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e5e7eb; text-align: left; }}
    th {{ background: #f9fafb; font-weight: 600; color: #374151; }}
    .badge {{ padding: 3px 9px; border-radius: 12px; font-size: 12px; font-weight: 600; }}
    .badge-xbar {{ background: #fee2e2; color: #b91c1c; }}
    .badge-cusum {{ background: #fef3c7; color: #b45309; }}
    .actions {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
    form.inline {{ display: flex; gap: 10px; flex-wrap: wrap; align-items: center; }}
    input[type="number"] {{ width: 92px; padding: 8px; border: 1px solid #d1d5db; border-radius: 6px; font-size: 14px; }}
    button {{ background: #1e3a8a; color: white; border: none; padding: 9px 16px; border-radius: 6px; cursor: pointer; font-weight: 600; font-size: 14px; }}
    button:hover {{ background: #1d4ed8; }}
    .btn-secondary {{ background: #4b5563; }}
    .btn-secondary:hover {{ background: #374151; }}
  </style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Manufacturing Quality Control Portal — CNC-Line-A</h1>
    <p>Project 9: Real-Time Shewhart (X̄–R) &amp; Two-Sided CUSUM Statistical Process Control</p>
  </div>

  <div class="grid">
    <div class="card"><h3>Total Batches</h3><div class="val">{data['total_batches']}</div></div>
    <div class="card"><h3>Baseline Mean (X̿)</h3><div class="val">{data['x_dbar']:.4f} mm</div></div>
    <div class="card"><h3>X̄ Out-of-Control Alerts</h3><div class="val alert">{data['xbar_alerts']}</div></div>
    <div class="card"><h3>CUSUM Drift Alerts</h3><div class="val alert">{data['cusum_alerts']}</div></div>
  </div>

  <div class="panel">
    <h2>Live Batch Inspection Simulator (Add 5-Part Subgroup)</h2>
    <p style="font-size:14px; color:#4b5563; margin-top:0;">
      Nominal Target = <strong>10.000 mm</strong> | Upper Control Limit (UCL) = <strong>{data['x_ucl']:.4f} mm</strong> | Lower Control Limit (LCL) = <strong>{data['x_lcl']:.4f} mm</strong>
    </p>
    <div class="actions">
      <form class="inline" method="POST" action="/add-batch">
        <input type="number" step="0.001" name="m1" value="10.080" required>
        <input type="number" step="0.001" name="m2" value="10.090" required>
        <input type="number" step="0.001" name="m3" value="10.070" required>
        <input type="number" step="0.001" name="m4" value="10.100" required>
        <input type="number" step="0.001" name="m5" value="10.080" required>
        <button type="submit">Inspect &amp; Log Batch</button>
      </form>
      <form method="POST" action="/reset">
        <button type="submit" class="btn-secondary">Reset to 200 Batches</button>
      </form>
    </div>
  </div>

  <div class="panel">
    <h2>Statistical Control Charts (X̄, R &amp; CUSUM)</h2>
    <img src="/chart" alt="SPC Control Charts">
  </div>

  <div class="panel">
    <h2>SQLite Control Alerts Log (Initial Triggers &amp; Live Submissions)</h2>
    <table>
      <thead><tr><th>Alert ID</th><th>Batch ID</th><th>Chart Type</th><th>Trigger Reason</th></tr></thead>
      <tbody>{alert_rows}</tbody>
    </table>
  </div>
</div>
</body>
</html>"""


class QCHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            html = render_page(get_dashboard_data()).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(html)))
            self.end_headers()
            self.wfile.write(html)
        elif self.path == "/chart":
            if CHART_PATH.exists():
                img = CHART_PATH.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "image/png")
                self.send_header("Content-Length", str(len(img)))
                self.end_headers()
                self.wfile.write(img)
            else:
                self.send_error(404, "Chart image not found")
        else:
            self.send_error(404)

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8")
        params = urllib.parse.parse_qs(body)

        if self.path == "/add-batch":
            vals = [float(params[f"m{i}"][0]) for i in range(1, 6)]
            x_bar = sum(vals) / 5.0
            r_val = max(vals) - min(vals)

            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            next_id = cur.execute(
                "SELECT COALESCE(MAX(batch_id), 0) + 1 FROM Sample_Batches"
            ).fetchone()[0]
            cur.execute(
                "INSERT INTO Sample_Batches (batch_id, line_id, recorded_time, is_baseline, batch_mean, batch_range) "
                "VALUES (?, 1, datetime('now'), 0, ?, ?)",
                (next_id, round(x_bar, 4), round(r_val, 4)),
            )
            for v in vals:
                cur.execute(
                    "INSERT INTO Measurements (batch_id, measured_value) VALUES (?, ?)",
                    (next_id, v),
                )
            ucl, lcl = cur.execute(
                "SELECT ucl, lcl FROM Control_Limits WHERE chart_type='X-bar'"
            ).fetchone()
            if x_bar > ucl or x_bar < lcl:
                cur.execute(
                    "INSERT INTO Control_Alerts (batch_id, chart_type, reason) VALUES (?, 'X-bar', ?)",
                    (next_id, f"Live 3-sigma breach (mean={x_bar:.4f})"),
                )
            conn.commit()
            conn.close()

        elif self.path == "/reset":
            subprocess.run(["py", "-3.12", str(BASE_DIR / "src" / "main.py")], check=True)

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", 5000), QCHandler)
    print("SPC Portal running at http://127.0.0.1:5000 (Press Ctrl+C to stop)")
    server.serve_forever()