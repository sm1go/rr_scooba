"""Advisor endpoints: help queue, conditions, employers, applications on
behalf of callers, follow-up overview, audit (spec section 3)."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import auth as auth_mod
from .. import db as db_mod
from ..clock import app_now
from ..db import get_conn
from pydantic import BaseModel

from ..models import (ApplicationIn, CallOutcomeIn, EmployerNewIn,
                      HelpRequestUpdate, WalkupTalkIn)
from ..serialize import _days_ago, help_request_out
from .jobs import mark_closed, mark_confirmed
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
    from ..serialize import STALE_DAYS
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
    # event conversations still unanswered after 7 days (spec v3 §8)
    talks = []
    for r in conn.execute(
            "SELECT t.*, u.name person_name, e.name emp_name,"
            " e.contact_email, e.contact_phone, e.contact_name"
            " FROM event_talk t LEFT JOIN user u ON u.id=t.user_id"
            " JOIN employer e ON e.id=t.employer_id"
            " WHERE t.status='talked' ORDER BY t.talked_at").fetchall():
        at = datetime.fromisoformat(r["talked_at"].replace("Z", "+00:00"))
        if at.tzinfo is None:
            at = at.replace(tzinfo=timezone.utc)
        days = (datetime.now(timezone.utc) - at).days
        if days > 7:
            talks.append({
                "id": r["id"],
                "person_name": r["person_name"] or r["visitor_name"],
                "recorded_by_advisor": r["user_id"] is None,
                "employer_name": r["emp_name"], "days_waiting": days,
                "employer": {"name": r["emp_name"],
                             "contact_name": r["contact_name"],
                             "contact_email": r["contact_email"],
                             "contact_phone": r["contact_phone"]}})
    return {"open_jobs": open_jobs, "stale_jobs": stale,
            "waiting_over_7_days": waiting, "new_help_requests": new_requests,
            "applications_by_status": by_status,
            "event_talks_unanswered": talks,
            "outcomes": {"last_7_days": _outcomes(conn, 7),
                         "all_time": _outcomes(conn, None)}}


CALL_OUTCOMES = ("still_open", "filled", "no_answer", "no_vacancy")


def _outcomes(conn: sqlite3.Connection, days: int | None) -> dict:
    """Aggregate counts only — never per person or per advisor."""
    def since(col: str) -> str:
        return (f" AND julianday({col}) >= julianday('now','-{days} days')"
                if days else "")

    def count(sql: str) -> int:
        return conn.execute(sql).fetchone()[0]

    hr = {r["status"]: r["c"] for r in conn.execute(
        "SELECT status, COUNT(*) c FROM help_request WHERE 1=1"
        + since("created_at") + " GROUP BY status")}
    calls = dict.fromkeys(CALL_OUTCOMES, 0)
    for r in conn.execute("SELECT detail FROM audit_log WHERE"
                          " action='call_logged'" + since("created_at")):
        o = r["detail"].rsplit(":", 1)[-1]
        if o in calls:
            calls[o] += 1
    contract = conn.execute(
        "SELECT SUM(hires_required) req, SUM(hires_done) done"
        " FROM procurement_contract").fetchone()
    return {
        "help_requests": {k: hr.get(k, 0)
                          for k in ("new", "in_progress", "done")},
        "contract_hires": {"done": contract["done"] or 0,
                           "required": contract["req"] or 0},
        "applications": count("SELECT COUNT(*) FROM application WHERE 1=1"
                              + since("created_at")),
        "applications_by_advisor": count(
            "SELECT COUNT(*) FROM application WHERE created_by_advisor=1"
            + since("created_at")),
        "interviews": count(
            "SELECT COUNT(*) FROM application WHERE status IN"
            " ('interview','offer')" + since("updated_at")),
        "offers": count("SELECT COUNT(*) FROM application WHERE"
                        " status='offer'" + since("updated_at")),
        "event_talks": {
            "recorded": count("SELECT COUNT(*) FROM event_talk WHERE 1=1"
                              + since("talked_at")),
            "answered": count("SELECT COUNT(*) FROM event_talk WHERE"
                              " status='answered'" + since("answered_at")),
            "unanswered": count("SELECT COUNT(*) FROM event_talk WHERE"
                                " status='talked'" + since("talked_at"))},
        "employer_calls": calls}


@router.post("/advisor/calls", status_code=201)
def log_call(payload: CallOutcomeIn,
             conn: sqlite3.Connection = Depends(get_conn),
             user=Depends(auth_mod.current_user)):
    """Outcome of a call to an employer. 'still_open' confirms the job,
    'filled' closes it; the audit row holds ids + outcome only."""
    _advisor(user)
    emp_id = payload.employer_id
    if payload.job_id:
        job = conn.execute("SELECT employer_id FROM job WHERE id=?",
                           (payload.job_id,)).fetchone()
        if not job:
            raise HTTPException(404, "Job not found.")
        emp_id = job["employer_id"]
    elif payload.outcome in ("still_open", "filled"):
        raise HTTPException(422, "Choose the job this answer is about.")
    if not emp_id or not conn.execute("SELECT 1 FROM employer WHERE id=?",
                                      (emp_id,)).fetchone():
        raise HTTPException(404, "Employer not found.")
    if payload.outcome == "still_open":
        mark_confirmed(conn, payload.job_id, user["id"])
    elif payload.outcome == "filled":
        mark_closed(conn, payload.job_id, user["id"])
    db_mod.audit(conn, user["id"], "call_logged",
                 f"{emp_id}:{payload.job_id or '-'}:{payload.outcome}")
    conn.commit()
    return {"employer_id": emp_id, "job_id": payload.job_id,
            "outcome": payload.outcome}


def _last_calls(conn: sqlite3.Connection) -> dict:
    out = {}
    for r in conn.execute("SELECT detail, created_at FROM audit_log"
                          " WHERE action='call_logged' ORDER BY id"):
        parts = r["detail"].split(":")
        if len(parts) == 3:
            out[parts[0]] = {"outcome": parts[2], "at": r["created_at"],
                             "job_id": None if parts[1] == "-" else parts[1]}
    return out


@router.get("/advisor/employers-to-call")
def employers_to_call(conn: sqlite3.Connection = Depends(get_conn),
                      user=Depends(auth_mod.current_user)):
    """Hidden-vacancy call list: no open job, newest confirmation older
    than 30 days, or the last call went unanswered. An employer who
    answered in the last 30 days drops off until then."""
    _advisor(user)
    calls = _last_calls(conn)
    order = {"call_again": 0, "no_open_job": 1, "stale": 2}
    out = []
    for e in conn.execute("SELECT * FROM employer ORDER BY name").fetchall():
        jobs = conn.execute(
            "SELECT id, status, confirmed_at FROM job WHERE employer_id=?"
            " ORDER BY status='open' DESC, confirmed_at DESC, created_at DESC",
            (e["id"],)).fetchall()
        open_days = [_days_ago(j["confirmed_at"]) for j in jobs
                     if j["status"] == "open"]
        newest = min((d for d in open_days if d is not None), default=None)
        call = calls.get(e["id"])
        if call and call["outcome"] == "no_answer":
            reason = "call_again"
        elif call and (_days_ago(call["at"]) or 0) <= 30:
            continue
        elif not open_days:
            reason = "no_open_job"
        elif newest is None or newest > 30:
            reason = "stale"
        else:
            continue
        out.append({
            "id": e["id"], "name": e["name"], "contact_name": e["contact_name"],
            "contact_email": e["contact_email"],
            "contact_phone": e["contact_phone"], "reason": reason,
            "open_jobs": len(open_days), "newest_confirmed_days_ago": newest,
            "latest_job_id": ((call and call["job_id"])
                              or (jobs[0]["id"] if jobs else None)),
            "last_call": ({"outcome": call["outcome"], "at": call["at"]}
                          if call else None)})
    out.sort(key=lambda r: order[r["reason"]])
    return {"employers": out}


@router.post("/advisor/event/talks", status_code=201)
def record_walkup_talk(payload: WalkupTalkIn,
                       conn: sqlite3.Connection = Depends(get_conn),
                       user=Depends(auth_mod.current_user)):
    """A walk-up visitor with no account or number talked to an employer;
    the advisor records it with the visitor's spoken consent so the
    employer still has to answer."""
    _advisor(user)
    if not payload.consent:
        raise HTTPException(422, "Ask the visitor first: they must agree "
                                 "that their name and contact are shared "
                                 "with this employer.")
    ev = conn.execute("SELECT id FROM event WHERE ends_at >= ? ORDER BY date LIMIT 1", (app_now(conn).isoformat(timespec='seconds'),)).fetchone()
    if not ev or not conn.execute(
            "SELECT 1 FROM employer_event WHERE event_id=? AND employer_id=?",
            (ev["id"], payload.employer_id)).fetchone():
        raise HTTPException(404, "That employer is not at the event.")
    if payload.job_id and not conn.execute(
            "SELECT 1 FROM job WHERE id=? AND employer_id=?",
            (payload.job_id, payload.employer_id)).fetchone():
        raise HTTPException(404, "That job is not from this employer.")
    talk_id = db_mod.new_id(conn, "et")
    conn.execute(
        "INSERT INTO event_talk (id,event_id,user_id,employer_id,job_id,"
        "visitor_name,visitor_contact_method,visitor_contact_value,"
        "recorded_by,consent,status,talked_at)"
        " VALUES (?,?,NULL,?,?,?,?,?,?,1,'talked',?)",
        (talk_id, ev["id"], payload.employer_id, payload.job_id,
         payload.first_name.strip(), payload.contact_method,
         payload.contact_value.strip(), user["id"],
         datetime.now(timezone.utc).isoformat(timespec="seconds")))
    db_mod.audit(conn, user["id"], "event_talk_walkup", talk_id)
    conn.commit()
    return {"id": talk_id, "employer_id": payload.employer_id,
            "job_id": payload.job_id, "status": "talked",
            "recorded_by_advisor": True}


@router.get("/advisor/event-overview")
def event_overview(conn: sqlite3.Connection = Depends(get_conn),
                   user=Depends(auth_mod.current_user)):
    """Per-booth counts for the event organiser, in booth order."""
    _advisor(user)
    ev = conn.execute("SELECT * FROM event WHERE ends_at >= ? ORDER BY date LIMIT 1", (app_now(conn).isoformat(timespec='seconds'),)).fetchone()
    if not ev:
        return {"event": None, "employers": [], "totals": None}

    def pct(a: int, b: int) -> int | None:
        return round(100 * a / b) if b else None

    sub = ("(SELECT COUNT(*) FROM event_talk t WHERE t.event_id=ee.event_id"
           " AND t.employer_id=e.id{})")
    rows = []
    for r in conn.execute(
            "SELECT e.id, e.name, ee.booth,"
            " (SELECT COUNT(*) FROM event_plan p WHERE p.event_id=ee.event_id"
            "  AND p.employer_id=e.id) planned, "
            + sub.format("") + " talks, "
            + sub.format(" AND t.status='answered'") + " answered, "
            + sub.format(" AND t.outcome='next_step'") + " next_step"
            " FROM employer_event ee JOIN employer e ON e.id=ee.employer_id"
            " WHERE ee.event_id=? ORDER BY ee.booth", (ev["id"],)):
        rows.append({
            "employer_id": r["id"], "name": r["name"], "booth": r["booth"],
            "visitors_planned": r["planned"], "talks": r["talks"],
            "answered": r["answered"], "next_step": r["next_step"],
            "answered_pct": pct(r["answered"], r["talks"])})
    totals = {k: sum(r[k] for r in rows) for k in
              ("visitors_planned", "talks", "answered", "next_step")}
    totals["answered_pct"] = pct(totals["answered"], totals["talks"])
    return {"event": {"id": ev["id"], "name": ev["name"], "date": ev["date"]},
            "employers": rows, "totals": totals}


@router.get("/audit")
def audit_log(limit: int = Query(default=100, le=500),
              conn: sqlite3.Connection = Depends(get_conn),
              user=Depends(auth_mod.current_user)):
    _advisor(user)
    rows = conn.execute(
        "SELECT id,actor,action,detail,created_at FROM audit_log"
        " ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return {"events": [dict(r) for r in rows]}


# --- city contracts (työllistämisehto) + credential checks --------------------

@router.get("/advisor/contracts")
def advisor_contracts(conn: sqlite3.Connection = Depends(get_conn),
                      user=Depends(auth_mod.current_user)):
    _advisor(user)
    today = date.today()
    out = []
    for c in conn.execute(
            "SELECT c.*, e.name employer_name, e.contact_name,"
            " e.contact_phone, e.contact_email FROM procurement_contract c"
            " JOIN employer e ON e.id=c.employer_id"
            " ORDER BY c.due").fetchall():
        if c["hires_done"] >= c["hires_required"]:
            status = "done"
        elif (date.fromisoformat(c["due"]) - today).days <= 90:
            status = "behind"
        else:
            status = "on_track"
        open_jobs = conn.execute(
            "SELECT COUNT(*) n FROM job WHERE contract_id=?"
            " AND status='open'", (c["id"],)).fetchone()["n"]
        out.append({
            "id": c["id"], "title": c["title"], "due": c["due"],
            "starts": c["starts"], "ends": c["ends"],
            "value_eur": c["value_eur"],
            "hires_required": c["hires_required"],
            "hires_done": c["hires_done"], "status": status,
            "open_jobs": open_jobs,
            "target_groups": json.loads(c["target_groups"] or "[]"),
            "employer": {"id": c["employer_id"], "name": c["employer_name"],
                         "contact_name": c["contact_name"],
                         "contact_phone": c["contact_phone"],
                         "contact_email": c["contact_email"]},
        })
    return {"contracts": out}


class HireIn(BaseModel):
    hired_on: str
    note: str = ""


@router.post("/advisor/contracts/{contract_id}/hires", status_code=201)
def record_hire(contract_id: str, payload: HireIn,
                conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(auth_mod.current_user)):
    _advisor(user)
    con = conn.execute("SELECT * FROM procurement_contract WHERE id=?",
                       (contract_id,)).fetchone()
    if not con:
        raise HTTPException(404, "Contract not found.")
    try:
        date.fromisoformat(payload.hired_on)
    except ValueError:
        raise HTTPException(422, "Give the date as YYYY-MM-DD.")
    conn.execute(
        "INSERT INTO contract_hire (id,contract_id,hired_on,note,advisor_id)"
        " VALUES (?,?,?,?,?)",
        (db_mod.new_id(conn, "hire"), contract_id, payload.hired_on,
         payload.note.strip(), user["id"]))
    conn.execute(
        "UPDATE procurement_contract SET hires_done=hires_done+1 WHERE id=?",
        (contract_id,))
    # the note stays in the hire row only — audit keeps no personal details
    db_mod.audit(conn, user["id"], "contract_hire_recorded", contract_id)
    conn.commit()
    return {"hires_done": con["hires_done"] + 1,
            "hires_required": con["hires_required"]}


class CredentialIn(BaseModel):
    label: str


@router.post("/advisor/help-requests/{hr_id}/credential", status_code=201)
def confirm_document(hr_id: str, payload: CredentialIn,
                     conn: sqlite3.Connection = Depends(get_conn),
                     user=Depends(auth_mod.current_user)):
    _advisor(user)
    hr = conn.execute("SELECT * FROM help_request WHERE id=?",
                      (hr_id,)).fetchone()
    if not hr or hr["kind"] != "check_document" or not hr["user_id"]:
        raise HTTPException(404, "Document check request not found.")
    label = payload.label.strip()
    if not label:
        raise HTTPException(422, "The document label is required.")
    cred_id = db_mod.new_id(conn, "cred")
    conn.execute(
        "INSERT INTO credential (id,user_id,label,advisor_id,checked_at)"
        " VALUES (?,?,?,?,?)",
        (cred_id, hr["user_id"], label, user["id"],
         date.today().isoformat()))
    conn.execute(
        "UPDATE help_request SET status='done', advisor_id=?,"
        " advisor_reply=?, updated_at=datetime('now') WHERE id=?",
        (user["id"], f"Document seen and confirmed: {label}", hr_id))
    db_mod.audit(conn, user["id"], "credential_confirmed", cred_id)
    conn.commit()
    return {"id": cred_id, "label": label,
            "checked_at": date.today().isoformat()}
