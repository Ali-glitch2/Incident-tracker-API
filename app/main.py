import sqlite3
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="Incident Tracker API")

DATABASE_FILE = "incidents.db"
ALLOWED_SEVERITIES = ["low", "medium", "high", "critical"]


# The data a user must send to create or update an incident.
class Incident(BaseModel):
    title: str
    service: str
    severity: str  # one of ALLOWED_SEVERITIES


# ======================================================================
# DATABASE HELPERS
# ======================================================================

def get_connection():
    """Open a connection to the database file."""
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row  # lets us read columns by name: row["title"]
    return connection


def create_table():
    """Create the incidents table if it does not exist yet."""
    connection = get_connection()
    connection.execute("""
        CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            service TEXT NOT NULL,
            severity TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    connection.commit()
    connection.close()


# Run once, when the app starts.
create_table()


def find_incident(incident_id):
    """Get one incident from the database, or send back a 404 error."""
    connection = get_connection()
    row = connection.execute(
        "SELECT * FROM incidents WHERE id = ?",
        [incident_id],
    ).fetchone()
    connection.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return dict(row)


def check_severity(severity):
    """Send back a 400 error if the severity is not allowed."""
    if severity not in ALLOWED_SEVERITIES:
        raise HTTPException(
            status_code=400,
            detail=f"Severity must be one of: {ALLOWED_SEVERITIES}"
        )


# ======================================================================
# ENDPOINTS
# ======================================================================

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------- CREATE (SQL: INSERT) ----------
@app.post("/incidents", status_code=201)
def create_incident(incident: Incident):
    """Report a new incident. New incidents always start as "open"."""
    check_severity(incident.severity)
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    connection = get_connection()
    cursor = connection.execute(
        "INSERT INTO incidents (title, service, severity, status, created_at) VALUES (?, ?, ?, ?, ?)",
        [incident.title, incident.service, incident.severity, "open", created_at],
    )
    connection.commit()
    new_id = cursor.lastrowid
    connection.close()

    return find_incident(new_id)


# ---------- READ ALL (SQL: SELECT) ----------
@app.get("/incidents")
def list_incidents():
    """Show every incident."""
    connection = get_connection()
    rows = connection.execute("SELECT * FROM incidents").fetchall()
    connection.close()

    incidents = []
    for row in rows:
        incidents.append(dict(row))
    return incidents


# ---------- READ ONE (SQL: SELECT ... WHERE) ----------
@app.get("/incidents/{incident_id}")
def get_incident(incident_id: int):
    """Show one incident."""
    return find_incident(incident_id)


# ---------- UPDATE (SQL: UPDATE) ----------
@app.put("/incidents/{incident_id}")
def update_incident(incident_id: int, incident: Incident):
    """Change the title, service and severity of an incident."""
    find_incident(incident_id)  # sends a 404 if it does not exist
    check_severity(incident.severity)

    connection = get_connection()
    connection.execute(
        "UPDATE incidents SET title = ?, service = ?, severity = ? WHERE id = ?",
        [incident.title, incident.service, incident.severity, incident_id],
    )
    connection.commit()
    connection.close()

    return find_incident(incident_id)

# ---------- READ BY STATUS (SQL: SELECT ... WHERE) ----------
@app.get("/incidents/status/{status}")
def list_incidents_by_status(status: str):
    """Show only incidents with this status, e.g. open or resolved."""
    connection = get_connection()
    rows = connection.execute(
        "SELECT * FROM incidents WHERE status = ?",
        [status],
    ).fetchall()
    connection.close()

    incidents = []
    for row in rows:
        incidents.append(dict(row))
    return incidents


# ---------- RESOLVE (SQL: UPDATE) ----------
@app.put("/incidents/{incident_id}/resolve")
def resolve_incident(incident_id: int):
    """Mark an incident as resolved (fixed)."""
    find_incident(incident_id)  # sends a 404 if it does not exist

    connection = get_connection()
    connection.execute(
        "UPDATE incidents SET status = ? WHERE id = ?",
        ["resolved", incident_id],
    )
    connection.commit()
    connection.close()

    return find_incident(incident_id)


# ---------- DELETE (SQL: DELETE) ----------
@app.delete("/incidents/{incident_id}")
def delete_incident(incident_id: int):
    """Delete an incident."""
    find_incident(incident_id)  # sends a 404 if it does not exist

    connection = get_connection()
    connection.execute(
        "DELETE FROM incidents WHERE id = ?",
        [incident_id],
    )
    connection.commit()
    connection.close()

    return {"message": f"Deleted incident {incident_id}"}
