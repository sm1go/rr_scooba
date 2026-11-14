"""Employer endpoints: own profile, own jobs, received applications (spec 3)."""

from __future__ import annotations

import json
import sqlite3

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import auth as auth_mod
from .. import db as db_mod
from ..db import get_conn
from ..models import EmployerProfileIn, StatusIn
from ..serialize import application_out, job_out

router = APIRouter(prefix="/api", tags=["employer"])


def _employer(user) -> None:
    if user["role"] != "employer":
        raise HTTPException(403, "This is not available for your account.")
    if not user["employer_id"]:
        raise HTTPException(403, "Your account is not linked to a company.")


def _employer_out(conn: sqlite3.Connection, employer_id: str) -> dict:
    row = conn.execute("SELECT * FROM employer WHERE id=?",
                       (employer_id,)).fetchone()
    out = dict(row)
    ev = conn.execute(
        "SELECT e.name,e.date,e.venue,ee.booth FROM employer_event ee"
        " JOIN event e ON e.id=ee.event_id WHERE ee.employer_id=?",
        (employer_id,)).fetchone()
    out["event"] = ({"name": ev["name"], "date": ev["date"],
                     "venue": ev["venue"], "booth": ev["booth"]}
                    if ev else None)
    return out


@router.get("/employer")
def get_employer(conn: sqlite3.Connection = Depends(get_conn),
                 user=Depends(auth_mod.current_user)):
    _employer(user)
    return _employer_out(conn, user["employer_id"])


@router.put("/employer")
def put_employer(payload: EmployerProfileIn,
                 conn: sqlite3.Connection = Depends(get_conn),
                 user=Depends(auth_mod.current_user)):
    _employer(user)
    conn.execute(
        "UPDATE employer SET name=COALESCE(?,name), about=?, contact_name=?,"
        " contact_email=?, contact_phone=? WHERE id=?",
        (payload.name, payload.about, payload.contact_name,
         payload.contact_email, payload.contact_phone, user["employer_id"]))
    db_mod.audit(conn, user["id"], "employer_updated", user["employer_id"])
    conn.commit()
    return _employer_out(conn, user["employer_id"])


@router.get("/employer/jobs")
def employer_jobs(conn: sqlite3.Connection = Depends(get_conn),
                  user=Depends(auth_mod.current_user)):
    _employer(user)
    rows = conn.execute(
        "SELECT * FROM job WHERE employer_id=? ORDER BY created_at DESC",
        (user["employer_id"],)).fetchall()
    jobs = []
    for r in rows:
        j = job_out(conn, r)
        j["applications_count"] = conn.execute(
            "SELECT COUNT(*) c FROM application WHERE job_id=? AND status IN"
            " ('sent','interview')", (r["id"],)).fetchone()["c"]
        jobs.append(j)
    return {"jobs": jobs}


@router.get("/employer/applications")
def employer_applications(job_id: str | None = Query(default=None),
                          conn: sqlite3.Connection = Depends(get_conn),
                          user=Depends(auth_mod.current_user)):
    _employer(user)
    sql = ("SELECT a.* FROM application a JOIN job j ON j.id = a.job_id"
           " WHERE j.employer_id=?")
    args: list = [user["employer_id"]]
    if job_id:
        if not conn.execute("SELECT 1 FROM job WHERE id=? AND employer_id=?",
                            (job_id, user["employer_id"])).fetchone():
            raise HTTPException(403, "This is not your job.")
        sql += " AND a.job_id=?"
        args.append(job_id)
    sql += " ORDER BY a.created_at DESC"
    rows = conn.execute(sql, args).fetchall()
    return {"applications": [application_out(conn, r, employer_view=True)
                             for r in rows]}


@router.post("/applications/{app_id}/status")
def set_application_status(app_id: str, payload: StatusIn,
                           conn: sqlite3.Connection = Depends(get_conn),
                           user=Depends(auth_mod.current_user)):
    row = conn.execute(
        "SELECT a.*, j.employer_id FROM application a JOIN job j"
        " ON j.id = a.job_id WHERE a.id=?", (app_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Application not found.")
    is_owner = user["role"] == "employer" \
        and user["employer_id"] == row["employer_id"]
    if not (is_owner or user["role"] == "advisor"):
        raise HTTPException(403, "This is not your application.")
    if not payload.status_note.strip():
        raise HTTPException(
            422, "A short note is required — say when and where for an "
                 "interview, or give a short reason.")
    if row["status"] not in ("sent", "interview"):
        raise HTTPException(409, "This application already has an answer.")
    # fair-hiring promises: backend enforces what the badges say
    commitments = json.loads(conn.execute(
        "SELECT commitments FROM job WHERE id=?",
        (row["job_id"],)).fetchone()["commitments"] or "[]")
    if "guaranteed_talk" in commitments and row["meets_must_haves"] \
            and row["status"] == "sent" and payload.status == "not_selected":
        raise HTTPException(
            409, "This job promises a conversation to everyone who meets "
                 "the must-haves. Offer a conversation first.")
    if "open_hiring" in commitments and payload.status == "offer":
        earlier = conn.execute(
            "SELECT 1 FROM application WHERE job_id=? AND status='sent'"
            " AND (created_at<? OR (created_at=? AND id<?)) LIMIT 1",
            (row["job_id"], row["created_at"], row["created_at"],
             row["id"])).fetchone()
        if earlier:
            raise HTTPException(
                409, "Open hiring: answer people in sign-up order. "
                     "Someone signed up before this person.")
    conn.execute(
        "UPDATE application SET status=?, status_note=?,"
        " updated_at=datetime('now') WHERE id=?",
        (payload.status, payload.status_note, app_id))
    db_mod.audit(conn, user["id"], "application_status",
                 f"{app_id}:{payload.status}")
    conn.commit()
    return application_out(conn, conn.execute(
        "SELECT * FROM application WHERE id=?", (app_id,)).fetchone(),
        employer_view=True)
