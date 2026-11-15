"""Demo-mode controls (spec §9.5): a movable clock plus a full reset.

demo_advance() simulates the *other* employers — never Sanna's company,
never a resident's own choices. Everything it writes carries
simulated=1 so the UI can mark it. It is idempotent: re-running at the
same stage is a no-op.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .. import db as db_mod, settings
from ..clock import app_now, event_phase, set_demo_now
from ..db import get_conn
from .events import book_if_mutual

router = APIRouter(prefix="/api/demo", tags=["demo"])

E1 = "ev-2027-03"
SANNA_EMP = "emp-cafe-koivu"
STAGES = ("registration", "matching_closed", "live", "after")
NEXT_KINDS = ["interview", "tryout", "call"]
NO_REASONS = [
    "We need someone who can start earlier.",
    "The role needs more experience than we thought.",
    "Our shifts do not fit the times you can work.",
]
YES_NOTES = [
    "Good talk — we would like to continue.",
    "You showed just what we need.",
    "Let us take the next step together.",
]


def _demo():
    if not settings.demo_mode():
        raise HTTPException(404, "Not found.")


def _get_event(conn, event_id: str):
    ev = conn.execute("SELECT * FROM event WHERE id=?",
                      (event_id,)).fetchone()
    if not ev:
        raise HTTPException(404, "Event not found.")
    return ev


class ClockIn(BaseModel):
    stage: str
    event_id: str = E1


def _stage_now(ev: sqlite3.Row, stage: str) -> datetime:
    sa = datetime.fromisoformat(ev["starts_at"])
    ea = datetime.fromisoformat(ev["ends_at"])
    mc = (datetime.fromisoformat(ev["matching_closes"])
          if ev["matching_closes"] else sa)
    if stage == "registration":
        return sa - timedelta(days=21)
    if stage == "matching_closed":
        return mc + timedelta(hours=1)
    if stage == "live":
        return sa + timedelta(hours=1, minutes=35)
    if stage == "after":
        return ea + timedelta(days=2)
    raise HTTPException(422, "Unknown stage.")


def _stable(*parts: str) -> int:
    return int(hashlib.md5("|".join(parts).encode()).hexdigest()[:8], 16)


def _advance_matching(conn, ev) -> None:
    """Employers (not Sanna's) invite people who chose them and ticked
    every must-have, stable order, up to free slots; then booking runs."""
    eid = ev["id"]
    for ee in conn.execute(
            "SELECT * FROM employer_event WHERE event_id=? AND"
            " employer_id != ?", (eid, SANNA_EMP)):
        eid_ = ee["employer_id"]
        card = json.loads(ee["need_card"] or "{}")
        n_must = len(card.get("must_haves") or [])
        used = conn.execute(
            "SELECT COUNT(*) c FROM event_invite WHERE event_id=?"
            " AND employer_id=?", (eid, eid_)).fetchone()["c"]
        free = ee["slots"] - used
        if free <= 0:
            continue
        cands = []
        for r in conn.execute(
                "SELECT r.id rid, r.user_id uid, p.meets FROM"
                " talent_registration r JOIN event_plan p"
                " ON p.user_id=r.user_id AND p.event_id=r.event_id"
                " WHERE r.event_id=? AND r.status='registered'"
                " AND p.employer_id=? AND NOT EXISTS ("
                "   SELECT 1 FROM event_invite i WHERE i.event_id=?"
                "   AND i.employer_id=? AND i.registration_id=r.id)",
                (eid, eid_, eid, eid_)):
            meets = set(json.loads(r["meets"] or "[]"))
            if meets >= set(range(n_must)):
                cands.append((r["rid"], r["uid"]))
        cands.sort(key=lambda x: _stable(eid_, x[1]))
        for rid, uid in cands[:free]:
            conn.execute(
                "INSERT OR IGNORE INTO event_invite (event_id,"
                "employer_id,registration_id,simulated,created_at)"
                " VALUES (?,?,?,1,?)",
                (eid, eid_, rid, app_now(conn).isoformat(
                    timespec="seconds")))
            book_if_mutual(conn, eid, eid_, uid)


def _advance_live(conn, ev, now: datetime) -> None:
    """Meetings that already ended (not Sanna's) get a recorded talk."""
    eid = ev["id"]
    slot = ev["slot_minutes"] or 10
    for m in conn.execute(
            "SELECT * FROM event_meeting WHERE event_id=? AND"
            " status='booked' AND employer_id != ?",
            (eid, SANNA_EMP)):
        start = datetime.fromisoformat(m["starts_at"])
        if start + timedelta(minutes=slot) > now:
            continue
        ee = conn.execute(
            "SELECT * FROM employer_event WHERE event_id=?"
            " AND employer_id=?", (eid, m["employer_id"])).fetchone()
        card = json.loads(ee["need_card"] or "{}") if ee else {}
        observed = (card.get("first_week") or [])[:2]
        h = _stable(m["id"])
        next_step = h % 5 < 3                       # ~60%
        talked = start + timedelta(minutes=slot)
        emp = conn.execute("SELECT address FROM employer WHERE id=?",
                           (m["employer_id"],)).fetchone()
        if next_step:
            outcome = "next_step"
            kind = NEXT_KINDS[h % 3]
            n_days = 3 + h % 4
            next_at = (datetime.fromisoformat(ev["date"])
                       + timedelta(days=n_days,
                                   hours=10)).isoformat(timespec="seconds")
            place = (emp["address"] if emp and emp["address"]
                     else "video call")
            note = YES_NOTES[h % len(YES_NOTES)]
        else:
            outcome = "not_now"
            kind, next_at, place = None, None, ""
            note = NO_REASONS[h % len(NO_REASONS)]
        conn.execute(
            "INSERT OR IGNORE INTO event_talk (id,event_id,user_id,"
            "employer_id,meeting_id,observed,status,outcome,"
            "employer_note,talked_at,next_kind,next_at,next_place,"
            "simulated) VALUES (?,?,?,?,?,?,'talked',?,?,?,?,?,?,1)",
            (db_mod.new_id(conn, "et"), eid, m["user_id"],
             m["employer_id"], m["id"], json.dumps(observed,
                                                 ensure_ascii=False),
             outcome, note, talked.isoformat(timespec="seconds"),
             kind, next_at, place))
        conn.execute(
            "UPDATE event_meeting SET status='done' WHERE id=?",
            (m["id"],))


def _advance_after(conn, ev) -> None:
    """Simulated talks get their answers sent (1–3 days after the event)."""
    ends = datetime.fromisoformat(ev["ends_at"])
    for t in conn.execute(
            "SELECT id FROM event_talk WHERE event_id=? AND simulated=1"
            " AND status='talked'", (ev["id"],)):
        h = _stable(t["id"])
        answered = (ends + timedelta(days=1 + h % 3,
                                     hours=10)).isoformat(
                                         timespec="seconds")
        conn.execute(
            "UPDATE event_talk SET status='answered', answered_at=?"
            " WHERE id=?", (answered, t["id"]))


def demo_advance(conn, ev, now: datetime) -> None:
    phase = event_phase(ev, conn, now)
    if phase in ("matched", "live", "after", "closed"):
        _advance_matching(conn, ev)
    if phase in ("live", "after", "closed"):
        _advance_live(conn, ev, now)
    if phase in ("after", "closed"):
        _advance_after(conn, ev)


@router.get("/state")
def demo_state(event_id: str = E1,
               conn: sqlite3.Connection = Depends(get_conn)):
    _demo()
    ev = _get_event(conn, event_id)
    now = app_now(conn)
    return {"now": now.isoformat(timespec="seconds"),
            "stage": event_phase(ev, conn, now)}


@router.post("/clock")
def demo_clock(payload: ClockIn,
               conn: sqlite3.Connection = Depends(get_conn)):
    _demo()
    ev = _get_event(conn, payload.event_id)
    now = _stage_now(ev, payload.stage)
    set_demo_now(conn, now)
    demo_advance(conn, ev, now)
    conn.commit()
    return {"now": now.isoformat(timespec="seconds"),
            "stage": payload.stage,
            "phase": event_phase(ev, conn, now)}


@router.post("/reset")
def demo_reset():
    _demo()
    db_mod.rebuild_db()
    return {"ok": True}
