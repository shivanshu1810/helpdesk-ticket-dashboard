# Helpdesk Ticket Dashboard

A small helpdesk ticketing dashboard written in Python using **only the standard library** — no installs, no frameworks. It shows the view a Tier 1 service desk analyst works from: how many tickets are open, what is urgent, and a simple way to log a new ticket.

![Screenshot placeholder: dashboard showing ticket counts by status, a priority table, the ticket list, and the create-ticket form](screenshot-placeholder.png)
*Screenshot placeholder — run the app (below), open the dashboard in a browser, and replace this image with a real screenshot of your running copy.*

## What it does

- **Dashboard counts** — ticket totals by status (Open, In Progress, Resolved, Closed) and by priority (Low, Medium, High, Critical)
- **Ticket list** — every ticket with ID, title, requester, priority, status, and created time
- **Create-ticket form** — new tickets are saved to a local SQLite database and appear on the dashboard immediately
- **Seed data** — six clearly fictional sample tickets (e.g. "Cannot sign in to Microsoft 365", "Printer on floor 2 not printing") so the dashboard is useful on first run

## How to run

You only need Python 3 (3.10 or newer recommended). Nothing to install.

```bash
cd helpdesk-ticket-dashboard
python app.py
```

Then open **http://localhost:8000** in your browser. Press `Ctrl+C` in the terminal to stop it.

- Data is stored in `tickets.db` (SQLite) in this folder, created automatically on first run.
- To reset to the seed tickets, stop the app and delete `tickets.db`, then run it again.
- To use a different port: `PORT=8080 python app.py` (PowerShell: `$env:PORT=8080; python app.py`)

## How it works

- `app.py` — everything in one file: an `http.server` web server, SQLite storage via `sqlite3`, and HTML rendered on the server
- `GET /` renders the dashboard; `POST /create` handles the form and redirects back to the dashboard
- User input is HTML-escaped before it is shown, and form values for status/priority are checked against allowed lists

## Skills demonstrated

- Python fundamentals: HTTP servers, form handling, and SQLite queries with the standard library only
- Helpdesk workflow concepts: ticket statuses, priorities, requesters, and queue counts
- Basic web safety habits: escaping user input and validating form values

## Limitations (honest notes)

This is a learning/portfolio project, not a production helpdesk system: there is no login, no assignment or SLA tracking, and it is designed to run locally on one machine.

## About

Recent Computer Systems Technician – Networking graduate (Georgian College, 2026) with Tier 1 Service Desk Analyst co-op experience at Royal Victoria Regional Health Centre, supporting Windows 11, Microsoft 365, Active Directory, and Halo ITSM. This dashboard mirrors, in miniature, the ticket queue view used in that work.
