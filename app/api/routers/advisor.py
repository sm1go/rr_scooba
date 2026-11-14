"""Advisor endpoints: help queue, conditions, employers, applications on
behalf of callers, follow-up overview, audit (spec section 3)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import auth as auth_mod
from .. import db as db_mod
from ..db import get_conn
from ..models import ApplicationIn, EmployerNewIn, HelpRequestUpdate
from ..serialize import application_out, help_request_out
from .resident import _create_application

router = APIRouter(prefix="/api", tags=["advisor"])


def _advisor(user) -> None:
    if user["role"] != "advisor":
        raise HTTPException(403, "This is not available for your account.")


@router.get("/advisor/help-requests")
def help_requests(status: str | None = Query(default=None),
                  conn: sqlite3.Connection = Depends(get_conn),
                  user=Depends(auth_mod.current_user)):
    _advisor(user)
    sql = "SELECT * FROM help_request"
    args: list = []
    if status:
        sql += " WHERE status=?"
        args.append(status)
    sql += " ORDER BY created_at DESC"
    rows = conn.execute(sql, args).fetchall()
    out = []
    for r in rows:
        h = help_request_out(r)
        if r["job_id"]:
            j = conn.execute("SELECT title, employer_id FROM job WHERE id=?",
                             (r["job_id"],)).fetchone()
            if j:
                e = conn.execute(
                    "SELECT name, contact_name, contact_email, contact_phone"
                    " FROM employer WHERE id=?",
                    (j["employer_id"],)).fetchone()
                h["job"] = {
                    "id": r["job_id"], "title": j["title"],
                    "employer_name": e["name"] if e else "",
                    "employer_contact_name": e["contact_name"] if e else "",
                    "employer_contact_email": e["contact_email"] if e else "",
                    "employer_contact_phone": e["contact_phone"] if e else ""}
        out.append(h)
    return {"help_requests": out}


@router.post("/advisor/help-requests/{hr_id}")
def update_help_request(hr_id: str, payload: HelpRequestUpdate,
                        conn: sqlite3.Connection = Depends(get_conn),
                        user=Depends(auth_mod.current_user)):
    _advisor(user)
    row = conn.execute("SELECT * FROM help_request WHERE id=?",
                       (hr_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Help request not found.")
    conn.execute(
        "UPDATE help_request SET status=?, advisor_reply=?, advisor_id=?,"
        " updated_at=datetime('now') WHERE id=?",
        (payload.status, payload.advisor_reply, user["id"], hr_id))
    db_mod.audit(conn, user["id"], "help_request_updated",
                 f"{hr_id}:{payload.status}")
    conn.commit()
    return help_request_out(conn.execute(
        "SELECT * FROM help_request WHERE id=?", (hr_id,)).fetchone())


@router.post("/advisor/employers", status_code=201)
def add_employer(payload: EmployerNewIn,
                 conn: sqlite3.Connection = Depends(get_conn),
                 user=Depends(auth_mod.current_user)):
    """Add an employer that has no account."""
    _advisor(user)
    emp_id = db_mod.new_id(conn, "emp")
    conn.execute(
        "INSERT INTO employer (id,name,about,contact_name,contact_email,"
        "contact_phone) VALUES (?,?,?,?,?,?)",
        (emp_id, payload.name, payload.about, payload.contact_name,
         payload.contact_email, payload.contact_phone))
    db_mod.audit(conn, user["id"], "employer_created", emp_id)
    conn.commit()
    return dict(conn.execute("SELECT * FROM employer WHERE id=?",
                             (emp_id,)).fetchone())


@router.post("/advisor/applications", status_code=201)
def advisor_application(payload: ApplicationIn,
                        conn: sqlite3.Connection = Depends(get_conn),
                        user=Depends(auth_mod.current_user)):
    """Apply on behalf of a walk-in or phone caller (consent required)."""
    _advisor(user)
    return _create_application(conn, payload, user=user, by_advisor=True)


@router.get("/advisor/overview")
def overview(conn: sqlite3.Connection = Depends(get_conn),
             user=Depends(auth_mod.current_user)):
    _advisor(user)
    open_jobs = conn.execute(
        "SELECT COUNT(*) c FROM job WHERE status='open'").fetchone()["c"]
    from ..serialize import STALE_DAYS, _days_ago
    stale = []
    for r in conn.execute("SELECT id,title,confirmed_at,employer_id FROM job"
                          " WHERE status='open'").fetchall():
        days = _days_ago(r["confirmed_at"])
        if days is not None and days > STALE_DAYS:
            e = conn.execute("SELECT name FROM employer WHERE id=?",
                             (r["employer_id"],)).fetchone()
            stale.append({"id": r["id"], "title": r["title"],
                          "employer_name": e["name"] if e else "",
                          "confirmed_days_ago": days})
    waiting = []
    cutoff = datetime.now(timezone.utc) - timedelta(days=7)
    for r in conn.execute(
            "SELECT a.*, j.title jt, j.employer_id FROM application a"
            " JOIN job j ON j.id=a.job_id"
            " WHERE a.status IN ('sent','interview')"
            " ORDER BY a.created_at").fetchall():
        created = datetime.fromisoformat(
            r["created_at"].replace("Z", "+00:00"))
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        if created < cutoff:
            e = conn.execute(
                "SELECT name,contact_email,contact_phone FROM employer"
                " WHERE id=?", (r["employer_id"],)).fetchone()
            waiting.append({
                "id": r["id"], "job_id": r["job_id"], "job_title": r["jt"],
                "applicant_name": r["name"], "status": r["status"],
                "days_waiting": (datetime.now(timezone.utc) - created).days,
                "employer": dict(e) if e else None})
    new_requests = conn.execute(
        "SELECT COUNT(*) c FROM help_request WHERE status='new'"
        ).fetchone()["c"]
    by_status = {r["status"]: r["c"] for r in conn.execute(
        "SELECT status, COUNT(*) c FROM application GROUP BY status")}
    return {"open_jobs": open_jobs, "stale_jobs": stale,
            "waiting_over_7_days": waiting, "new_help_requests": new_requests,
            "applications_by_status": by_status}


@router.get("/audit")
def audit_log(limit: int = Query(default=100, le=500),
              conn: sqlite3.Connection = Depends(get_conn),
              user=Depends(auth_mod.current_user)):
    _advisor(user)
    rows = conn.execute(
        "SELECT id,actor,action,detail,created_at FROM audit_log"
        " ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return {"events": [dict(r) for r in rows]}
