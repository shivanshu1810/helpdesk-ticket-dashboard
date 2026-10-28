#!/usr/bin/env python3
"""
Helpdesk Ticket Dashboard
A tiny ticketing dashboard using only the Python standard library.
Run:  python app.py
Open: http://localhost:8000
Data is stored in tickets.db (SQLite) next to this file. Delete that file
to reset to the seed sample tickets.
Author: Shivanshu Sharma - portfolio project.
"""
import html
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tickets.db")
PORT = int(os.environ.get("PORT", "8000"))
STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
PRIORITIES = ["Low", "Medium", "High", "Critical"]

SEED_TICKETS = [
    ("Cannot sign in to Microsoft 365", "User reports repeated password prompts in Outlook.", "High", "Open", "Alex Example"),
    ("Laptop running very slowly", "Boot takes over five minutes; disk checks requested.", "Medium", "In Progress", "Priya Example"),
    ("New starter laptop setup", "Image laptop and install standard software before Monday.", "Medium", "Open", "Sam Example"),
    ("Printer on floor 2 not printing", "Queue shows jobs stuck; spooler restart did not clear it.", "Low", "Resolved", "Jordan Example"),
    ("VPN drops every few minutes", "Remote user loses connection on home Wi-Fi.", "High", "In Progress", "Taylor Example"),
    ("Request access to shared drive", "Manager approval received; add user to department group.", "Low", "Closed", "Morgan Example"),
]

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL DEFAULT '',
            priority TEXT NOT NULL DEFAULT 'Medium',
            status TEXT NOT NULL DEFAULT 'Open',
            requester TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""")
    count = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    if count == 0:
        conn.executemany(
            "INSERT INTO tickets (title, description, priority, status, requester) VALUES (?,?,?,?,?)",
            SEED_TICKETS,
        )
    conn.commit()
    conn.close()

def esc(value):
    return html.escape(str(value or ""))

def render_dashboard():
    conn = get_conn()
    tickets = conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
    by_status = {s: conn.execute("SELECT COUNT(*) FROM tickets WHERE status=?", (s,)).fetchone()[0] for s in STATUSES}
    by_priority = {p: conn.execute("SELECT COUNT(*) FROM tickets WHERE priority=?", (p,)).fetchone()[0] for p in PRIORITIES}
    conn.close()

    status_cards = "".join(f'<div class="card"><h3>{esc(s)}</h3><p>{n}</p></div>' for s, n in by_status.items())
    priority_rows = "".join(f"<tr><td>{esc(p)}</td><td>{n}</td></tr>" for p, n in by_priority.items())
    ticket_rows = "".join(
        "<tr>"
        f"<td>#{t['id']}</td><td>{esc(t['title'])}</td><td>{esc(t['requester'])}</td>"
        f"<td>{esc(t['priority'])}</td><td>{esc(t['status'])}</td><td>{esc(t['created_at'])}</td>"
        "</tr>" for t in tickets
    ) or '<tr><td colspan="6">No tickets yet.</td></tr>'
    status_options = "".join(f'<option>{s}</option>' for s in STATUSES)
    priority_options = "".join(f'<option{" selected" if p=="Medium" else ""}>{p}</option>' for p in PRIORITIES)

    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Helpdesk Ticket Dashboard</title>
<style>
 body {{ font-family: system-ui, Arial, sans-serif; margin: 32px; color: #1f2937; }}
 h1 {{ margin-bottom: 4px; }} .sub {{ color: #6b7280; margin-top: 0; }}
 .cards {{ display: flex; gap: 12px; flex-wrap: wrap; margin: 20px 0; }}
 .card {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 14px 20px; min-width: 110px; }}
 .card h3 {{ margin: 0; font-size: 14px; color: #6b7280; }} .card p {{ margin: 6px 0 0; font-size: 28px; font-weight: 700; }}
 table {{ border-collapse: collapse; width: 100%; margin: 12px 0 28px; }}
 th, td {{ border: 1px solid #e5e7eb; padding: 8px 10px; text-align: left; font-size: 14px; }}
 th {{ background: #f9fafb; }}
 form {{ border: 1px solid #e5e7eb; border-radius: 10px; padding: 16px; max-width: 560px; }}
 label {{ display: block; margin: 10px 0 4px; font-weight: 600; font-size: 14px; }}
 input, textarea, select {{ width: 100%; padding: 8px; box-sizing: border-box; }}
 button {{ margin-top: 14px; padding: 9px 18px; background: #1d4ed8; color: #fff; border: 0; border-radius: 6px; cursor: pointer; }}
</style></head><body>
<h1>Helpdesk Ticket Dashboard</h1>
<p class="sub">Sample portfolio dashboard. Seed tickets are fictional examples.</p>
<h2>Tickets by status</h2><div class="cards">{status_cards}</div>
<h2>Tickets by priority</h2>
<table><tr><th>Priority</th><th>Count</th></tr>{priority_rows}</table>
<h2>All tickets</h2>
<table><tr><th>ID</th><th>Title</th><th>Requester</th><th>Priority</th><th>Status</th><th>Created</th></tr>{ticket_rows}</table>
<h2>Create a ticket</h2>
<form method="post" action="/create">
 <label>Title <input name="title" required></label>
 <label>Requester <input name="requester" required></label>
 <label>Description <textarea name="description" rows="3"></textarea></label>
 <label>Priority <select name="priority">{priority_options}</select></label>
 <label>Status <select name="status">{status_options}</select></label>
 <button type="submit">Create ticket</button>
</form>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/index.html"):
            self.send_error(404, "Not found")
            return
        body = render_dashboard().encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/create":
            self.send_error(404, "Not found")
            return
        length = int(self.headers.get("Content-Length", 0))
        data = parse_qs(self.rfile.read(length).decode("utf-8"))
        def field(name):
            return data.get(name, [""])[0].strip()
        title, requester = field("title"), field("requester")
        priority = field("priority") if field("priority") in PRIORITIES else "Medium"
        status = field("status") if field("status") in STATUSES else "Open"
        if title and requester:
            conn = get_conn()
            conn.execute(
                "INSERT INTO tickets (title, description, priority, status, requester) VALUES (?,?,?,?,?)",
                (title, field("description"), priority, status, requester),
            )
            conn.commit()
            conn.close()
        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))

if __name__ == "__main__":
    init_db()
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"Helpdesk dashboard running at http://localhost:{PORT}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
