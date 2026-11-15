"""Event mode: booth plan, visitor numbers, recorded conversations
(spec v3 §8)."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from .. import db as db_mod
from ..clock import app_now
from ..auth import current_user
from ..db import get_conn
from ..models import TalkAnswerIn, TalkIn

router = APIRouter(prefix="/api", tags=["event"])


def _resident(user):
    if user["role"] != "resident":
        raise HTTPException(403, "This is not available for your account.")


def _employer(user):
    if user["role"] != "employer" or not user["employer_id"]:
        raise HTTPException(403, "This is not available for your account.")


def _event(conn) -> sqlite3.Row | None:
    return conn.execute(
        "SELECT * FROM event WHERE ends_at >= ? ORDER BY date LIMIT 1",
        (app_now(conn).isoformat(timespec="seconds"),)).fetchone()


def _visitor_code(conn, user_id: str, event_id: str) -> str:
    """One 4-digit code per person per event, created on first use."""
    row = conn.execute(
        "SELECT code FROM event_visitor WHERE user_id=? AND event_id=?",
        (user_id, event_id)).fetchone()
    if row:
        return row["code"]
    import secrets
    for _ in range(20):
        code = f"{secrets.randbelow(10000):04d}"
        if not conn.execute(
                "SELECT 1 FROM event_visitor WHERE event_id=? AND code=?",
                (event_id, code)).fetchone():
            conn.execute(
                "INSERT INTO event_visitor (user_id,event_id,code)"
                " VALUES (?,?,?)", (user_id, event_id, code))
            return code
    raise HTTPException(500, "Could not create a visitor number.")


def _plan_out(conn, user_id: str, event_id: str) -> dict:
    """'My plan': visitor number + employers ordered by booth."""
    code = _visitor_code(conn, user_id, event_id)
    rows = conn.execute(
        "SELECT e.id, e.name, ee.booth FROM event_plan ep"
        " JOIN employer_event ee"
        "  ON ee.employer_id=ep.employer_id AND ee.event_id=ep.event_id"
        " JOIN employer e ON e.id=ep.employer_id"
        " WHERE ep.user_id=? AND ep.event_id=? ORDER BY ee.booth",
        (user_id, event_id)).fetchall()
    out = []
    for r in rows:
        jobs = [dict(j) for j in conn.execute(
            "SELECT id,title FROM job WHERE employer_id=? AND status='open'"
            " ORDER BY title", (r["id"],))]
        out.append({"employer_id": r["id"], "name": r["name"],
                    "booth": r["booth"], "jobs": jobs})
    return {"code": code, "booths": out}


def _talk_out(r) -> dict:
    return {"id": r["id"], "event_id": r["event_id"],
            "user_id": r["user_id"], "employer_id": r["employer_id"],
            "status": r["status"], "outcome": r["outcome"],
            "employer_note": r["employer_note"], "job_id": r["job_id"],
            "recorded_by_advisor": r["user_id"] is None,
            "talked_at": r["talked_at"], "answered_at": r["answered_at"]}


# --- resident ---------------------------------------------------------------

@router.get("/me/event-plan")
def my_plan(conn: sqlite3.Connection = Depends(get_conn),
            user=Depends(current_user)):
    _resident(user)
    ev = _event(conn)
    if not ev:
        return {"event": None, "code": None, "booths": []}
    out = _plan_out(conn, user["id"], ev["id"])
    conn.commit()
    return {"event": dict(ev), **out}


@router.put("/me/event-plan/{employer_id}", status_code=201)
def add_to_plan(employer_id: str,
                conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(current_user)):
    _resident(user)
    ev = _event(conn)
    if not ev:
        raise HTTPException(404, "There is no event right now.")
    if not conn.execute(
            "SELECT 1 FROM employer_event WHERE event_id=? AND employer_id=?",
            (ev["id"], employer_id)).fetchone():
        raise HTTPException(404, "That employer is not at the event.")
    conn.execute(
        "INSERT OR IGNORE INTO event_plan (user_id,event_id,employer_id)"
        " VALUES (?,?,?)", (user["id"], ev["id"], employer_id))
    db_mod.audit(conn, user["id"], "event_plan_add", employer_id)
    conn.commit()
    return {"event": dict(ev), **_plan_out(conn, user["id"], ev["id"])}


@router.delete("/me/event-plan/{employer_id}")
def remove_from_plan(employer_id: str,
                     conn: sqlite3.Connection = Depends(get_conn),
                     user=Depends(current_user)):
    _resident(user)
    ev = _event(conn)
    if not ev:
        raise HTTPException(404, "There is no event right now.")
    conn.execute("DELETE FROM event_plan WHERE user_id=? AND event_id=?"
                 " AND employer_id=?", (user["id"], ev["id"], employer_id))
    conn.commit()
    return {"event": dict(ev), **_plan_out(conn, user["id"], ev["id"])}


# --- employer -----------------------------------------------------------------

@router.get("/employer/event")
def employer_event(conn: sqlite3.Connection = Depends(get_conn),
                   user=Depends(current_user)):
    _employer(user)
    ev = _event(conn)
    if not ev:
        return {"event": None, "booth": None, "visitors_planned": 0,
                "talks": []}
    ee = conn.execute(
        "SELECT booth FROM employer_event WHERE event_id=? AND employer_id=?",
        (ev["id"], user["employer_id"])).fetchone()
    planned = conn.execute(
        "SELECT COUNT(*) c FROM event_plan WHERE event_id=? AND employer_id=?",
        (ev["id"], user["employer_id"])).fetchone()["c"]
    talks = [dict(_talk_out(r), **_person_brief(conn, r))
             for r in conn.execute(
                 "SELECT * FROM event_talk WHERE event_id=? AND employer_id=?"
                 " ORDER BY talked_at", (ev["id"], user["employer_id"]))]
    return {"event": dict(ev), "booth": ee["booth"] if ee else None,
            "visitors_planned": planned, "talks": talks}


def _person_brief(conn, talk) -> dict:
    """Name + preferred contact — revealed only after the number is used,
    or given with spoken consent to an advisor (walk-up visitor)."""
    if talk["user_id"] is None:
        return {"person_name": talk["visitor_name"],
                "person_contact_method": talk["visitor_contact_method"],
                "person_contact_value": talk["visitor_contact_value"]}
    user_id = talk["user_id"]
    u = conn.execute("SELECT name, email, phone FROM user WHERE id=?",
                     (user_id,)).fetchone()
    p = conn.execute(
        "SELECT contact_method FROM resident_profile WHERE user_id=?",
        (user_id,)).fetchone()
    method = (p["contact_method"] if p and p["contact_method"] else
              ("email" if u and u["email"] else "phone"))
    value = {"email": u["email"] if u else None,
             "phone": u["phone"] if u else None,
             "sms": u["phone"] if u else None}.get(method) or ""
    return {"person_name": u["name"] if u else "",
            "person_contact_method": method, "person_contact_value": value}


@router.post("/employer/event/talks", status_code=201)
def record_talk(payload: TalkIn,
                conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(current_user)):
    """'Record a conversation' — the visitor number reveals name + contact."""
    _employer(user)
    ev = _event(conn)
    if not ev or not conn.execute(
            "SELECT 1 FROM employer_event WHERE event_id=? AND employer_id=?",
            (ev["id"], user["employer_id"])).fetchone():
        raise HTTPException(404, "Your organisation has no booth at this event.")
    vis = conn.execute(
        "SELECT user_id FROM event_visitor WHERE event_id=? AND code=?",
        (ev["id"], payload.code)).fetchone()
    if not vis:
        raise HTTPException(404, "No visitor has that number. "
                                 "Check the number and try again.")
    if conn.execute(
            "SELECT 1 FROM event_talk WHERE event_id=? AND user_id=?"
            " AND employer_id=?",
            (ev["id"], vis["user_id"], user["employer_id"])).fetchone():
        raise HTTPException(409, "You already recorded a conversation "
                                 "with this visitor.")
    talk_id = db_mod.new_id(conn, "et")
    now = app_now(conn).isoformat(timespec="seconds")
    conn.execute(
        "INSERT INTO event_talk (id,event_id,user_id,employer_id,status,"
        "talked_at) VALUES (?,?,?,?,'talked',?)",
        (talk_id, ev["id"], vis["user_id"], user["employer_id"], now))
    from .events import _award_attended
    _award_attended(conn, ev["id"], vis["user_id"])
    db_mod.audit(conn, user["id"], "event_talk", talk_id)
    conn.commit()
    r = conn.execute("SELECT * FROM event_talk WHERE id=?",
                     (talk_id,)).fetchone()
    return {**_talk_out(r), **_person_brief(conn, r)}


@router.post("/employer/event/talks/{talk_id}/answer")
def answer_talk(talk_id: str, payload: TalkAnswerIn,
                conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(current_user)):
    """Every conversation gets an answer: next step or not now + a note."""
    _employer(user)
    r = conn.execute(
        "SELECT * FROM event_talk WHERE id=? AND employer_id=?",
        (talk_id, user["employer_id"])).fetchone()
    if not r:
        raise HTTPException(404, "Conversation not found.")
    if payload.outcome == "next_step" and not (
            payload.next_kind and payload.next_at):
        raise HTTPException(422, "A next step needs a kind and a "
                                 "date and time.")
    conn.execute(
        "UPDATE event_talk SET status='answered', outcome=?, employer_note=?,"
        " answered_at=?, next_kind=?, next_at=?, next_place=? WHERE id=?",
        (payload.outcome, payload.employer_note,
         app_now(conn).isoformat(timespec="seconds"), payload.next_kind,
         payload.next_at, payload.next_place or "", talk_id))
    from .events import _maybe_award_employer_answered
    _maybe_award_employer_answered(conn, r["event_id"], user["employer_id"])
    db_mod.audit(conn, user["id"], "event_talk_answered",
                 f"{talk_id}:{payload.outcome}")
    conn.commit()
    r = conn.execute("SELECT * FROM event_talk WHERE id=?",
                     (talk_id,)).fetchone()
    return {**_talk_out(r), **_person_brief(conn, r)}


# --- resident view of their talks (for /applications) -------------------------

@router.get("/me/event-talks")
def my_talks(conn: sqlite3.Connection = Depends(get_conn),
             user=Depends(current_user)):
    _resident(user)
    rows = conn.execute(
        "SELECT t.*, e.name employer_name FROM event_talk t"
        " JOIN employer e ON e.id=t.employer_id WHERE t.user_id=?"
        " ORDER BY t.talked_at DESC", (user["id"],)).fetchall()
    return {"talks": [{**_talk_out(r),
                       "employer_name": r["employer_name"]} for r in rows]}
