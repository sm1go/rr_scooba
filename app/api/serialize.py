"""Shared row -> API dict serializers. Every job response uses job_out() so
the output is identical for anonymous and signed-in callers."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timezone

from .rules.labels import haversine_km, job_labels

CONDITION_KEYS = [
    "step_free_entrance", "lift", "accessible_toilet", "seated_work",
    "flexible_breaks", "quiet_environment", "written_instructions",
    "sign_language_ok", "assistive_tech_ok", "adjustments_negotiable",
]

JOB_FIELDS = [
    "id", "employer_id", "title", "field", "duties", "address", "district",
    "lat", "lon", "work_mode", "pay_amount", "pay_unit", "pay_note", "shifts",
    "schedule_flexible", "hours_min", "hours_max", "contract", "experience",
    "experience_note", "qualifications", "onboarding", "languages", "lifting",
    "apply_question", "cv_required", "positions", "status", "source",
    "confirmed_at", "created_at",
]
_JSON_FIELDS = {"duties", "shifts", "qualifications", "languages"}
_BOOL_FIELDS = {"schedule_flexible", "cv_required"}
STALE_DAYS = 14


def conditions_out(conn: sqlite3.Connection, job_id: str) -> list[dict]:
    """All 10 keys; 'unknown' (no row) is part of the shape."""
    rows = {r["key"]: r for r in conn.execute(
        "SELECT key,value,source,checked_at,note FROM job_condition"
        " WHERE job_id=?", (job_id,))}
    out = []
    for key in CONDITION_KEYS:
        r = rows.get(key)
        if r:
            out.append({"key": key, "value": r["value"], "source": r["source"],
                        "checked_at": r["checked_at"], "note": r["note"]})
        else:
            out.append({"key": key, "value": "unknown", "source": None,
                        "checked_at": None, "note": ""})
    return out


def _days_ago(iso_date: str | None) -> int | None:
    if not iso_date:
        return None
    d = date.fromisoformat(iso_date[:10])
    return (date.today() - d).days


def job_out(conn: sqlite3.Connection, row: sqlite3.Row,
            district_center: tuple[float, float] | None = None) -> dict:
    job = {}
    for f in JOB_FIELDS:
        v = row[f]
        if f in _JSON_FIELDS:
            v = json.loads(v or "[]")
        elif f in _BOOL_FIELDS:
            v = bool(v)
        job[f] = v

    emp = conn.execute("SELECT id,name FROM employer WHERE id=?",
                       (job["employer_id"],)).fetchone()
    job["employer"] = {"id": emp["id"], "name": emp["name"]} if emp else None

    conds = conditions_out(conn, job["id"])
    job["conditions"] = conds
    known = sum(1 for c in conds if c["value"] != "unknown")
    job["labels"] = job_labels(job, known)

    ev = conn.execute(
        "SELECT e.name,e.date,e.venue,ee.booth FROM employer_event ee"
        " JOIN event e ON e.id = ee.event_id WHERE ee.employer_id=?",
        (job["employer_id"],)).fetchone()
    job["event"] = ({"name": ev["name"], "date": ev["date"],
                     "venue": ev["venue"], "booth": ev["booth"]}
                    if ev else None)

    days = _days_ago(job["confirmed_at"])
    job["confirmed_days_ago"] = days
    job["stale"] = days is not None and days > STALE_DAYS

    if district_center and job["lat"] is not None:
        job["distance_km"] = round(
            haversine_km(district_center[0], district_center[1],
                         job["lat"], job["lon"]), 1)
    return job


def application_out(conn: sqlite3.Connection, row: sqlite3.Row,
                    employer_view: bool = False) -> dict:
    app = {"id": row["id"], "job_id": row["job_id"],
           "name": row["name"], "contact_method": row["contact_method"],
           "contact_value": row["contact_value"],
           "availability_note": row["availability_note"],
           "answer": row["answer"],
           "shared_needs": json.loads(row["shared_needs"] or "[]"),
           "meet_at_event": bool(row["meet_at_event"]),
           "status": row["status"], "status_note": row["status_note"],
           "created_by_advisor": bool(row["created_by_advisor"]),
           "created_at": row["created_at"], "updated_at": row["updated_at"]}
    created = datetime.fromisoformat(row["created_at"].replace("Z", "+00:00"))
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    app["days_waiting"] = (datetime.now(timezone.utc) - created).days
    job = conn.execute("SELECT id,title,status FROM job WHERE id=?",
                       (row["job_id"],)).fetchone()
    emp = None
    if job:
        e = conn.execute("SELECT name FROM employer e JOIN job j"
                         " ON j.employer_id=e.id WHERE j.id=?",
                         (row["job_id"],)).fetchone()
        emp = e["name"] if e else None
        app["job"] = {"id": job["id"], "title": job["title"],
                      "status": job["status"], "employer_name": emp}
    if not employer_view:
        # history of status changes from the audit log
        app["history"] = [dict(r) for r in conn.execute(
            "SELECT action,detail,created_at FROM audit_log"
            " WHERE action='application_status' AND detail LIKE ?"
            " ORDER BY created_at", (f"{row['id']}:%",))]
    return app


def help_request_out(row: sqlite3.Row) -> dict:
    return {"id": row["id"], "user_id": row["user_id"], "name": row["name"],
            "contact_method": row["contact_method"],
            "contact_value": row["contact_value"], "job_id": row["job_id"],
            "kind": row["kind"],
            "condition_keys": json.loads(row["condition_keys"] or "[]"),
            "message": row["message"], "status": row["status"],
            "advisor_reply": row["advisor_reply"],
            "created_at": row["created_at"], "updated_at": row["updated_at"]}
