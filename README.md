# Incident Tracker API

A REST API built with **FastAPI** and **SQLite** to log and manage production incidents, such as "the website is slow" or "the database disk is full". Incidents are stored in a real database, so they survive restarts.

It implements full **CRUD** (Create, Read, Update, Delete) using plain SQL.

![Python](https://img.shields.io/badge/Python-3.13-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.165-009688?logo=fastapi&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-003B57?logo=sqlite&logoColor=white)

---

## Features

- Report, list, view, edit, resolve and delete incidents
- Filter incidents by status (`open` / `resolved`)
- Data stored in **SQLite**, persisted across restarts
- Severity validation (`low`, `medium`, `high`, `critical`)
- Parameterized SQL queries (`?` placeholders) to prevent SQL injection
- Proper HTTP status codes: `201`, `400`, `404`, `422`
- Interactive API docs at `/docs`

## API endpoints

| Method | Endpoint | Description | SQL used |
|--------|----------|-------------|----------|
| GET | `/health` | Health check | – |
| POST | `/incidents` | Report a new incident (starts as `open`) | `INSERT` |
| GET | `/incidents` | List all incidents | `SELECT` |
| GET | `/incidents/{id}` | Get one incident | `SELECT ... WHERE` |
| GET | `/incidents/status/{status}` | List incidents with a given status | `SELECT ... WHERE` |
| PUT | `/incidents/{id}` | Edit title, service and severity | `UPDATE` |
| PUT | `/incidents/{id}/resolve` | Mark an incident as resolved | `UPDATE` |
| DELETE | `/incidents/{id}` | Delete an incident | `DELETE` |

### Example: `POST /incidents`

Request body:
```json
{ "title": "Database disk is full", "service": "database", "severity": "critical" }
```

Response (`201 Created`):
```json
{
  "id": 2,
  "title": "Database disk is full",
  "service": "database",
  "severity": "critical",
  "status": "open",
  "created_at": "2026-11-20 21:48:52"
}
```

### Example: `PUT /incidents/2/resolve`

```json
{
  "id": 2,
  "title": "Database disk is full",
  "service": "database",
  "severity": "critical",
  "status": "resolved",
  "created_at": "2026-11-20 21:48:52"
}
```

### Error responses

| Code | When |
|------|------|
| `400` | Severity is not one of `low`, `medium`, `high`, `critical` |
| `404` | Incident id does not exist |
| `422` | A required field is missing or has the wrong type |

## Database

The app creates `incidents.db` automatically on first start, with this table:

| Column | Type | Notes |
|--------|------|-------|
| `id` | INTEGER | Primary key, auto-increment |
| `title` | TEXT | Required |
| `service` | TEXT | Required |
| `severity` | TEXT | `low` / `medium` / `high` / `critical` |
| `status` | TEXT | `open` or `resolved` |
| `created_at` | TEXT | Set by the server |

The database file is listed in `.gitignore`, so each environment keeps its own data.

## Project structure

```
incident-tracker-api/
├── app/
│   ├── __init__.py     # Marks "app" as a Python package
│   └── main.py         # API endpoints and database code
├── requirements.txt
├── .gitignore
└── README.md
```

## Getting started

### Prerequisites
- Python 3.10 or newer (SQLite is included with Python)

### Installation

```bash
git clone https://github.com/Ali-glitch2/Incident-tracker-API.git
cd Incident-tracker-API

python -m venv .venv
# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Run

```bash
uvicorn app.main:app --reload
```

Open **http://127.0.0.1:8000/docs** to try every endpoint in the browser.

## Usage with curl

```bash
# Report an incident
curl -X POST http://127.0.0.1:8000/incidents \
  -H "Content-Type: application/json" \
  -d '{"title": "Website is slow", "service": "web", "severity": "high"}'

# List open incidents
curl http://127.0.0.1:8000/incidents/status/open

# Resolve incident 1
curl -X PUT http://127.0.0.1:8000/incidents/1/resolve

# Delete incident 1
curl -X DELETE http://127.0.0.1:8000/incidents/1
```

**Windows PowerShell:**

```powershell
$body = @{ title = "Website is slow"; service = "web"; severity = "high" } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/incidents -ContentType "application/json" -Body $body
Invoke-RestMethod -Method Put -Uri http://127.0.0.1:8000/incidents/1/resolve
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Want to start with an empty database | Stop the server and delete `incidents.db`. It is recreated on the next start |
| `database is locked` | Another program (e.g. a DB viewer) has the file open. Close it |
| Endpoints return unexpected `404`s | Another process may be using port 8000. Check with `Get-NetTCPConnection -LocalPort 8000` (Windows) or `ss -tlnp` (Linux) |

## Roadmap

- [ ] Add `resolved_at` timestamp
- [ ] Pagination for large incident lists
- [ ] Authentication (only logged-in users can report or resolve)
- [ ] Switch to PostgreSQL for production
- [ ] Docker image

## What I learned

- Storing data in a **SQLite** database instead of memory
- Writing SQL: `CREATE TABLE`, `INSERT`, `SELECT`, `UPDATE`, `DELETE`
- Why `commit()` is needed to save changes
- Preventing **SQL injection** with `?` placeholders
- Using **PUT** for updates to complete full CRUD
- Why function names must be unique in Python

---

Built as **Day 3** of a 7-day FastAPI & backend challenge.
