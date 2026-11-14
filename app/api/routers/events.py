"""Event-centred mode (spec v4): events hub data, need cards, talent
registration, mutual-interest booking, organizer board.

Existing single-event endpoints (spec v3 §8) stay in routers/event.py and
keep pointing at the earliest event (the treffit demo)."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException

from .. import db as db_mod
from ..auth import current_user, optional_user
from ..db import SEED_DIR, get_conn
from ..models import (MeetingTalkIn, VisitorCodeIn,EventCardNeedIn, EventInviteIn, EventRegisterIn,
                      InterestIn, OrgNeedIn, RegistrationPatch)
from ..rules import lint
from ..rules.labels import haversine_km

router = APIRouter(prefix="/api", tags=["events"])

INTEREST_LIMIT = 5
CEFR = ["A1", "A2", "B1", "B2", "C1", "C2"]


def _today() -> date:
    """Module-level so tests can freeze 'today' via monkeypatch."""
    return date.today()


def _resident(user):
    if user["role"] != "resident":
        raise HTTPException(403, "This is not available for your account.")


def _employer(user):
    if user["role"] != "employer" or not user["employer_id"]:
        raise HTTPException(403, "This is not available for your account.")


def _advisor(user):
    if user["role"] != "advisor":
        raise HTTPException(403, "This is not available for your account.")


def _get_event(conn, event_id: str) -> sqlite3.Row:
    ev = conn.execute("SELECT * FROM event WHERE id=?", (event_id,)).fetchone()
    if not ev:
        raise HTTPException(404, "Event not found.")
    return ev


def event_phase(ev: sqlite3.Row, today: date | None = None) -> str:
    """registration | needs_published | today | finished."""
    today = today or _today()
    day = date.fromisoformat(ev["date"])
    if today > day:
        return "finished"
    if today == day:
        return "today"
    if ev["publish_date"] and today >= date.fromisoformat(ev["publish_date"]):
        return "needs_published"
    return "registration"


def _event_out(ev: sqlite3.Row, conn) -> dict:
    employers = conn.execute(
        "SELECT COUNT(*) c FROM employer_event WHERE event_id=?",
        (ev["id"],)).fetchone()["c"]
    registered = conn.execute(
        "SELECT COUNT(*) c FROM talent_registration WHERE event_id=?"
        " AND status='registered'", (ev["id"],)).fetchone()["c"]
    return {"id": ev["id"], "name": ev["name"], "date": ev["date"],
            "format": ev["format"], "language": ev["language"],
            "starts_at": ev["starts_at"], "ends_at": ev["ends_at"],
            "venue": ev["venue"], "address": ev["address"],
            "description": ev["description"],
            "programme": json.loads(ev["programme"] or "[]"),
            "capacity": ev["capacity"], "slot_minutes": ev["slot_minutes"],
            "need_deadline": ev["need_deadline"],
            "publish_date": ev["publish_date"],
            "time_groups": json.loads(ev["time_groups"] or "[]"),
            "phase": event_phase(ev), "employer_count": employers,
            "registered": registered}


def _need_out(ee: sqlite3.Row) -> dict | None:
    if not ee["need_card"]:
        return None
    card = json.loads(ee["need_card"])
    return {"card": card, "submitted_at": ee["need_submitted_at"],
            "by": ee["need_by"]}


def _published(ev: sqlite3.Row) -> bool:
    if not ev["publish_date"]:
        return True                  # no publish gate on this event
    return _today() >= date.fromisoformat(ev["publish_date"])


def _registration(conn, event_id: str, user_id: str):
    return conn.execute(
        "SELECT * FROM talent_registration WHERE event_id=? AND user_id=?"
        " AND status != 'cancelled'", (event_id, user_id)).fetchone()


def _district_center(district_id: str) -> tuple[float, float] | None:
    cat = json.loads((SEED_DIR / "catalog.json").read_text(encoding="utf-8"))
    d = next((d for d in cat["districts"] if d["id"] == district_id), None)
    return (d["lat"], d["lon"]) if d else None


def _employer_district(conn, employer_id: str) -> str | None:
    r = conn.execute(
        "SELECT district FROM job WHERE employer_id=? AND district != ''"
        " AND status='open' LIMIT 1", (employer_id,)).fetchone()
    return r["district"] if r else None


# --- booking -------------------------------------------------------------------

def _meeting_window(ev: sqlite3.Row) -> list[tuple[int, int]]:
    """One-to-one programme windows as (start_min, end_min) pairs."""
    out = []
    for p in json.loads(ev["programme"] or "[]"):
        if p.get("kind") != "one_to_one":
            continue
        s = int(p["start"][:2]) * 60 + int(p["start"][3:5])
        e = int(p["end"][:2]) * 60 + int(p["end"][3:5])
        out.append((s, e))
    return out


def _slot_starts(ev: sqlite3.Row) -> list[str]:
    """All slot start times in the one_to_one windows, HH:MM."""
    step = ev["slot_minutes"] or 10
    out = []
    for s, e in _meeting_window(ev):
        t = s
        while t + step <= e:
            out.append(f"{t // 60:02d}:{t % 60:02d}")
            t += step
    return out


def book_if_mutual(conn: sqlite3.Connection, event_id: str,
                   employer_id: str, user_id: str) -> dict | None:
    """Book a meeting when the talent's interest and the employer's invite
    are mutual. Earliest free slot inside the one_to_one window at or after
    the person's time-group entry; a person never has two meetings at the
    same time and an employer never two in one slot. Returns the meeting
    or None when it stays mutual without a slot."""
    ev = _get_event(conn, event_id)
    reg = _registration(conn, event_id, user_id)
    if not reg or reg["status"] != "registered":
        return None
    interested = conn.execute(
        "SELECT 1 FROM event_plan WHERE event_id=? AND employer_id=?"
        " AND user_id=?", (event_id, employer_id, user_id)).fetchone()
    invited = conn.execute(
        "SELECT 1 FROM event_invite WHERE event_id=? AND employer_id=?"
        " AND registration_id=?", (event_id, employer_id,
                                  reg["id"])).fetchone()
    if not (interested and invited):
        return None
    if conn.execute(
            "SELECT 1 FROM event_meeting WHERE event_id=? AND employer_id=?"
            " AND user_id=? AND status != 'cancelled'",
            (event_id, employer_id, user_id)).fetchone():
        return None                       # exactly one meeting per pair

    groups = {g["id"]: g for g in json.loads(ev["time_groups"] or "[]")}
    entry = (groups.get(reg["time_group"]) or {}).get("entry", "00:00")
    hhmm = lambda iso: iso.split("T")[1][:5]
    busy_person = {hhmm(r["starts_at"]) for r in conn.execute(
        "SELECT starts_at FROM event_meeting WHERE event_id=? AND user_id=?"
        " AND status != 'cancelled'", (event_id, user_id))}
    busy_employer = {hhmm(r["starts_at"]) for r in conn.execute(
        "SELECT starts_at FROM event_meeting WHERE event_id=? AND"
        " employer_id=? AND status != 'cancelled'",
        (event_id, employer_id))}
    for slot in _slot_starts(ev):
        if slot < entry:
            continue
        if slot in busy_person or slot in busy_employer:
            continue
        mid = db_mod.new_id(conn, "mt")
        starts = f"{ev['date']}T{slot}:00"
        conn.execute(
            "INSERT INTO event_meeting (id,event_id,employer_id,user_id,"
            "registration_id,starts_at,status)"
            " VALUES (?,?,?,?,?,?,'booked')",
            (mid, event_id, employer_id, user_id, reg["id"], starts))
        return {"id": mid, "starts_at": starts, "status": "booked"}
    return None                           # mutual, no free slot


# --- fit reasons -----------------------------------------------------------------

def _slot_overlap(availability: list[str], ev: sqlite3.Row) -> bool:
    """Does any availability slot cover part of the one_to_one window?"""
    weekday = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"][
        date.fromisoformat(ev["date"]).weekday()]
    for s, e in _meeting_window(ev):
        mid = (s + e) // 2
        part = "morning" if mid < 12 * 60 else \
               "afternoon" if mid < 17 * 60 else "evening"
        if f"{weekday}-{part}" in availability:
            return True
    return False


def _credentials(conn, user_id: str) -> list[str]:
    return [r["label"] for r in conn.execute(
        "SELECT label FROM credential WHERE user_id=? ORDER BY checked_at",
        (user_id,))]


def _fit_reasons(conn, ev, employer_id: str, need_card: dict | None, reg,
                 meets: list[int], lang_levels: dict,
                 creds: list[str]) -> list[dict]:
    """Short reason keys + params; the UI translates. Never a score."""
    reasons = []
    if need_card:
        mhs = need_card.get("must_haves") or []
        if mhs:
            reasons.append({"key": "mh_met", "n": len(meets), "of": len(mhs)})
        for l in (need_card.get("languages") or [])[:2]:
            have = lang_levels.get(l.get("name"))
            if have and CEFR.index(have) >= CEFR.index(l.get("level", "A1")):
                reasons.append({"key": "lang_ok", "name": l["name"],
                                "level": have, "need": l["level"],
                                "task": l.get("task", "")})
    card = json.loads(reg["card"] or "{}")
    own = _district_center(card.get("district") or "")
    if own:
        emp_c = _district_center(
            _employer_district(conn, employer_id) or "")
        if emp_c:
            km = round(haversine_km(own[0], own[1], emp_c[0], emp_c[1]), 1)
            reasons.append({"key": "area_near"} if km < 0.5
                           else {"key": "area", "km": km})
    if creds:
        reasons.append({"key": "docs", "n": len(creds)})
    if _slot_overlap(card.get("availability") or [], ev):
        reasons.append({"key": "avail_overlap"})
    return reasons


# --- public event browsing -----------------------------------------------------

@router.get("/events")
def list_events(conn: sqlite3.Connection = Depends(get_conn)):
    rows = conn.execute("SELECT * FROM event ORDER BY date").fetchall()
    return {"events": [_event_out(ev, conn) for ev in rows]}


def _can_see_needs(conn, ev, user) -> bool:
    if _published(ev):
        return True
    if not user:
        return False
    if user["role"] in ("advisor", "employer"):
        return True
    return bool(_registration(conn, ev["id"], user["id"]))


def _need_cards(conn, ev, include_employer_names=True) -> list[dict]:
    out = []
    for ee in conn.execute(
            "SELECT ee.*, e.name emp_name, e.contact_name, e.contact_phone"
            " FROM employer_event ee JOIN employer e"
            " ON e.id=ee.employer_id WHERE ee.event_id=? ORDER BY ee.booth",
            (ev["id"],)):
        need = _need_out(ee)
        item = {"employer_id": ee["employer_id"], "booth": ee["booth"],
                "slots": ee["slots"],
                "formats": json.loads(ee["formats"] or "[]"),
                "need": need}
        if include_employer_names:
            item["employer_name"] = ee["emp_name"]
        out.append(item)
    return out


@router.get("/events/{event_id}")
def event_detail(event_id: str,
                 conn: sqlite3.Connection = Depends(get_conn),
                 user=Depends(optional_user)):
    ev = _get_event(conn, event_id)
    employers = _need_cards(conn, ev)
    if not _can_see_needs(conn, ev, user):
        for e in employers:
            e["need"] = None
    return {**_event_out(ev, conn), "needs_published": _published(ev),
            "employers": employers}


@router.get("/events/{event_id}/needs")
def need_cards(event_id: str,
               conn: sqlite3.Connection = Depends(get_conn),
               user=Depends(optional_user)):
    """Published need cards; a signed-in registered talent also gets the
    server-computed fit reasons on each card."""
    ev = _get_event(conn, event_id)
    if not _can_see_needs(conn, ev, user):
        raise HTTPException(403, "The need cards are published on "
                                 + ev["publish_date"] + ".")
    reg = (_registration(conn, event_id, user["id"])
           if user and user["role"] == "resident" else None)
    my_plans = {}
    creds = []
    if reg:
        creds = _credentials(conn, reg["user_id"])
        for p in conn.execute(
                "SELECT employer_id,meets,language_levels FROM event_plan"
                " WHERE event_id=? AND user_id=?",
                (event_id, user["id"])):
            my_plans[p["employer_id"]] = p
    out = []
    for item in _need_cards(conn, ev):
        if not item["need"]:
            continue
        p = my_plans.get(item["employer_id"])
        if reg:
            item["fit"] = _fit_reasons(
                conn, ev, item["employer_id"], item["need"]["card"], reg,
                json.loads(p["meets"]) if p else [],
                json.loads(p["language_levels"]) if p else {}, creds)
            item["interested"] = p is not None
            item["meets"] = json.loads(p["meets"]) if p else []
            item["language_levels"] = (json.loads(p["language_levels"])
                                       if p else {})
        out.append(item)
    return {"event": _event_out(ev, conn), "cards": out}


# --- talent registration + interests ---------------------------------------------

@router.post("/events/{event_id}/register", status_code=201)
def register(event_id: str, payload: EventRegisterIn,
             conn: sqlite3.Connection = Depends(get_conn),
             user=Depends(current_user)):
    _resident(user)
    ev = _get_event(conn, event_id)
    if event_phase(ev) in ("today", "finished"):
        raise HTTPException(409, "Registration for this event has closed.")
    if _registration(conn, event_id, user["id"]):
        raise HTTPException(409, "You are already registered for this event.")
    groups = {g["id"] for g in json.loads(ev["time_groups"] or "[]")}
    if payload.time_group not in groups:
        raise HTTPException(422, "Choose a time group.")
    card = payload.card.model_dump()
    if not (1 <= len(card["done"]) <= 3):
        raise HTTPException(422, "Write 1–3 things you have done.")
    reg_id = db_mod.new_id(conn, "tr")
    taken = conn.execute(
        "SELECT COUNT(*) c FROM talent_registration WHERE event_id=?"
        " AND status='registered'", (event_id,)).fetchone()["c"]
    status = "registered" if not ev["capacity"] or taken < ev["capacity"] \
        else "waitlist"
    conn.execute(
        "INSERT INTO talent_registration (id,event_id,user_id,time_group,"
        "status,card_language,card,created_at) VALUES (?,?,?,?,?,?,?,?)",
        (reg_id, event_id, user["id"], payload.time_group, status,
         payload.card_language, json.dumps(card, ensure_ascii=False),
         datetime.now(timezone.utc).isoformat(timespec="seconds")))
    db_mod.audit(conn, user["id"], "event_registered",
                 f"{event_id}:{status}")
    conn.commit()
    return {"registration": _reg_out(conn, reg_id)}


@router.patch("/events/{event_id}/register")
def update_registration(event_id: str, payload: RegistrationPatch,
                        conn: sqlite3.Connection = Depends(get_conn),
                        user=Depends(current_user)):
    _resident(user)
    reg = _registration(conn, event_id, user["id"])
    if not reg:
        raise HTTPException(404, "You are not registered for this event.")
    if payload.card is not None:
        conn.execute(
            "UPDATE talent_registration SET card=? WHERE id=?",
            (json.dumps(payload.card.model_dump(), ensure_ascii=False),
             reg["id"]))
    if payload.card_language is not None:
        conn.execute(
            "UPDATE talent_registration SET card_language=? WHERE id=?",
            (payload.card_language, reg["id"]))
    conn.commit()
    return {"registration": _reg_out(conn, reg["id"])}


@router.delete("/events/{event_id}/register")
def cancel_registration(event_id: str,
                        conn: sqlite3.Connection = Depends(get_conn),
                        user=Depends(current_user)):
    _resident(user)
    reg = _registration(conn, event_id, user["id"])
    if not reg:
        raise HTTPException(404, "You are not registered for this event.")
    conn.execute(
        "UPDATE talent_registration SET status='cancelled' WHERE id=?",
        (reg["id"],))
    conn.commit()
    return {"ok": True}


def _reg_out(conn, reg_id: str) -> dict:
    r = conn.execute("SELECT * FROM talent_registration WHERE id=?",
                     (reg_id,)).fetchone()
    return {"id": r["id"], "event_id": r["event_id"],
            "time_group": r["time_group"], "status": r["status"],
            "card_language": r["card_language"],
            "card": json.loads(r["card"] or "{}"),
            "created_at": r["created_at"]}


@router.get("/events/{event_id}/my")
def my_event(event_id: str,
             conn: sqlite3.Connection = Depends(get_conn),
             user=Depends(current_user)):
    _resident(user)
    reg = _registration(conn, event_id, user["id"])
    interests = [dict(r) for r in conn.execute(
        "SELECT p.employer_id, p.meets, p.language_levels, e.name"
        " FROM event_plan p JOIN employer e ON e.id=p.employer_id"
        " WHERE p.event_id=? AND p.user_id=? ORDER BY e.name",
        (event_id, user["id"]))]
    for i in interests:
        i["meets"] = json.loads(i["meets"])
        i["language_levels"] = json.loads(i["language_levels"])
    meetings = _my_meetings(conn, event_id, user["id"])
    for m in meetings:
        ee = _ee(conn, event_id, m["employer_id"])
        card = json.loads(ee["need_card"]) if ee and ee["need_card"] else {}
        m["need_line"] = (card.get("first_week") or [""])[0]
    queue = [dict(r) for r in conn.execute(
        "SELECT q.employer_id, q.status, q.joined_at, e.name employer_name"
        " FROM event_queue q JOIN employer e ON e.id=q.employer_id"
        " WHERE q.event_id=? AND q.user_id=? AND q.status != 'left'"
        " ORDER BY q.joined_at", (event_id, user["id"]))]
    ev = _get_event(conn, event_id)
    entry = {g["id"]: g for g in
             json.loads(ev["time_groups"] or "[]")}
    code = conn.execute(
        "SELECT code FROM event_visitor WHERE event_id=? AND user_id=?",
        (event_id, user["id"])).fetchone()
    talks = []
    for tr in conn.execute(
            "SELECT t.id, t.employer_id, t.status, t.outcome,"
            " t.employer_note, e.name employer_name FROM event_talk t"
            " JOIN employer e ON e.id=t.employer_id"
            " WHERE t.event_id=? AND t.user_id=?"
            " ORDER BY t.talked_at", (event_id, user["id"])):
        talks.append({"id": tr["id"], "employer_id": tr["employer_id"],
                      "employer_name": tr["employer_name"],
                      "status": tr["status"],
                      "outcome": tr["outcome"],
                      "note": tr["employer_note"]})
    return {"event": _event_out(_get_event(conn, event_id), conn),
            "registration": _reg_out(conn, reg["id"]) if reg else None,
            "interests": interests, "meetings": meetings, "talks": talks,
            "queue": queue,
            "entry": (reg and entry.get(reg["time_group"], {})
                      .get("entry")),
            "visitor_code": code["code"] if code else None,
            "interest_limit": INTEREST_LIMIT}


def _my_meetings(conn, event_id: str, user_id: str) -> list[dict]:
    out = []
    for m in conn.execute(
            "SELECT m.*, e.name employer_name, ee.booth"
            " FROM event_meeting m JOIN employer e ON e.id=m.employer_id"
            " LEFT JOIN employer_event ee"
            " ON ee.event_id=m.event_id AND ee.employer_id=m.employer_id"
            " WHERE m.event_id=? AND m.user_id=? AND m.status != 'cancelled'"
            " ORDER BY m.starts_at", (event_id, user_id)):
        out.append({"id": m["id"], "employer_id": m["employer_id"],
                    "employer_name": m["employer_name"],
                    "booth": m["booth"], "starts_at": m["starts_at"],
                    "status": m["status"]})
    return out


@router.put("/events/{event_id}/interests/{employer_id}", status_code=201)
def add_interest(event_id: str, employer_id: str, payload: InterestIn,
                 conn: sqlite3.Connection = Depends(get_conn),
                 user=Depends(current_user)):
    _resident(user)
    _get_event(conn, event_id)
    if not _registration(conn, event_id, user["id"]):
        raise HTTPException(403, "Register for the event first.")
    ee = conn.execute(
        "SELECT need_card FROM employer_event WHERE event_id=?"
        " AND employer_id=?", (event_id, employer_id)).fetchone()
    if not ee:
        raise HTTPException(404, "That employer is not at this event.")
    if not conn.execute(
            "SELECT 1 FROM event_plan WHERE event_id=? AND employer_id=?"
            " AND user_id=?", (event_id, employer_id, user["id"])).fetchone():
        n = conn.execute(
            "SELECT COUNT(*) c FROM event_plan WHERE event_id=? AND user_id=?",
            (event_id, user["id"])).fetchone()["c"]
        if n >= INTEREST_LIMIT:
            raise HTTPException(409, "You can pick at most "
                                   f"{INTEREST_LIMIT} employers.")
    mh = (json.loads(ee["need_card"]).get("must_haves") or []) \
        if ee["need_card"] else []
    meets = [i for i in payload.meets if 0 <= i < len(mh)]
    conn.execute(
        "INSERT OR REPLACE INTO event_plan (user_id,event_id,employer_id,"
        "meets,language_levels) VALUES (?,?,?,?,?)",
        (user["id"], event_id, employer_id,
         json.dumps(meets), json.dumps(payload.language_levels)))
    meeting = book_if_mutual(conn, event_id, employer_id, user["id"])
    db_mod.audit(conn, user["id"], "event_interest",
                 f"{event_id}:{employer_id}")
    conn.commit()
    return {"meeting": meeting}


@router.delete("/events/{event_id}/interests/{employer_id}")
def remove_interest(event_id: str, employer_id: str,
                    conn: sqlite3.Connection = Depends(get_conn),
                    user=Depends(current_user)):
    _resident(user)
    conn.execute("DELETE FROM event_plan WHERE event_id=? AND employer_id=?"
                 " AND user_id=?", (event_id, employer_id, user["id"]))
    conn.commit()
    return {"ok": True}


# --- employer workspace ----------------------------------------------------------

def _check_need_card(card: dict) -> None:
    """Shape rules + the job-ad wording checker on all free text."""
    fw = card.get("first_week") or []
    if not (1 <= len(fw) <= 5):
        raise HTTPException(422, "Write 1–5 first-week items.")
    mhs = card.get("must_haves") or []
    if len(mhs) > 3:
        raise HTTPException(422, "At most 3 must-haves.")
    for m in mhs:
        if not (m.get("why") or "").strip():
            raise HTTPException(422, "Every must-have needs a 'why'.")
    if len(card.get("languages") or []) > 2:
        raise HTTPException(422, "At most 2 language needs.")
    job_like = {
        "title": "", "pay_note": "", "experience_note": "",
        "onboarding": "", "apply_question": "", "lifting": "",
        "duties": fw,
        "qualifications": [m.get("text", "") for m in mhs]
        + [m.get("why", "") for m in mhs]
        + list(card.get("will_teach") or []),
        "languages": [{"language": l.get("name"), "level": l.get("level"),
                       "task": l.get("task")}
                      for l in card.get("languages") or []],
    }
    issues = lint.blocking_issues(job_like)
    # need cards also refuse explicit native-level language asks
    for tip_id, pattern, why, suggestion in lint.TIPS:
        if tip_id != "native_language":
            continue
        rx = re.compile(pattern, re.I)
        for field in ("qualifications", "duties"):
            for text in job_like.get(field) or []:
                m = rx.search(text)
                if m:
                    issues.append({"rule": tip_id, "field": field,
                                   "trigger": m.group(0), "why": why,
                                   "suggestion": suggestion})
                    break
    if issues:
        raise HTTPException(422, {"message": "The wording must be fixed "
                                           "before submitting.",
                                  "issues": issues})


def _ee(conn, event_id: str, employer_id: str):
    return conn.execute(
        "SELECT * FROM employer_event WHERE event_id=? AND employer_id=?",
        (event_id, employer_id)).fetchone()


@router.put("/employer/events/{event_id}", status_code=201)
def join_event(event_id: str, payload: dict | None = None,
               conn: sqlite3.Connection = Depends(get_conn),
               user=Depends(current_user)):
    _employer(user)
    _get_event(conn, event_id)
    body = payload or {}
    slots = int(body.get("slots", 8))
    formats = [f for f in body.get("formats", ["one_to_one"])
               if f in ("one_to_one", "walk_in", "pitch")]
    if conn.execute("SELECT 1 FROM employer_event WHERE event_id=?"
                    " AND employer_id=?",
                    (event_id, user["employer_id"])).fetchone():
        conn.execute(
            "UPDATE employer_event SET slots=?, formats=? WHERE event_id=?"
            " AND employer_id=?",
            (slots, json.dumps(formats), event_id, user["employer_id"]))
    else:
        conn.execute(
            "INSERT INTO employer_event (employer_id,event_id,booth,slots,"
            "formats) VALUES (?,?,?,?,?)",
            (user["employer_id"], event_id, body.get("booth", ""), slots,
             json.dumps(formats)))
    db_mod.audit(conn, user["id"], "event_joined", event_id)
    conn.commit()
    return employer_workspace(event_id, conn, user)


@router.put("/employer/events/{event_id}/need")
def submit_need(event_id: str, payload: EventCardNeedIn,
                conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(current_user)):
    _employer(user)
    card = payload.model_dump(exclude_none=True)
    _check_need_card(card)
    for jid in card.get("job_ids") or []:
        if not conn.execute(
                "SELECT 1 FROM job WHERE id=? AND employer_id=?",
                (jid, user["employer_id"])).fetchone():
            raise HTTPException(422, "You can only link your own jobs.")
    ee = _ee(conn, event_id, user["employer_id"])
    if not ee:
        raise HTTPException(404, "Join the event first.")
    conn.execute(
        "UPDATE employer_event SET need_card=?, need_submitted_at=?,"
        " need_by='employer' WHERE event_id=? AND employer_id=?",
        (json.dumps(card, ensure_ascii=False),
         date.today().isoformat(), event_id, user["employer_id"]))
    db_mod.audit(conn, user["id"], "event_need", f"{event_id}:employer")
    conn.commit()
    return employer_workspace(event_id, conn, user)


def _anon_card(conn, ev, reg, ee_row, employer_id: str,
               interested_reg_ids: set[str]) -> dict:
    """Anonymous talent card for one employer — never a name, contact or
    user id; the registration id is the card id."""
    card = json.loads(reg["card"] or "{}")
    need = json.loads(ee_row["need_card"]) if ee_row["need_card"] else {}
    plan = conn.execute(
        "SELECT meets, language_levels FROM event_plan WHERE event_id=?"
        " AND employer_id=? AND user_id=?",
        (ev["id"], employer_id, reg["user_id"])).fetchone()
    meets = json.loads(plan["meets"]) if plan else []
    langs = json.loads(plan["language_levels"]) if plan else {}
    creds = _credentials(conn, reg["user_id"])
    return {
        "id": reg["id"],
        "done": card.get("done") or [],
        "looking_for": card.get("looking_for", ""),
        "district": card.get("district", ""),
        "availability": card.get("availability") or [],
        "time_group": reg["time_group"],
        "interested": reg["id"] in interested_reg_ids,
        "meets": meets,
        "language_levels": langs,
        "credentials": creds,
        "fit": _fit_reasons(conn, ev, employer_id, need, reg, meets, langs, creds),
    }


@router.get("/employer/events/{event_id}/cards")
def anonymous_cards(event_id: str, all: bool = False,
                    conn: sqlite3.Connection = Depends(get_conn),
                    user=Depends(current_user)):
    """Anonymous talent cards, random but stable order per employer.
    Default: only people who chose this employer."""
    _employer(user)
    ev = _get_event(conn, event_id)
    ee = _ee(conn, event_id, user["employer_id"])
    if not ee:
        raise HTTPException(404, "Join the event first.")
    interested = {r["registration_id"] for r in conn.execute(
        "SELECT tr.id AS registration_id FROM event_plan p"
        " JOIN talent_registration tr"
        " ON tr.event_id=p.event_id AND tr.user_id=p.user_id"
        " WHERE p.event_id=? AND p.employer_id=? AND tr.status='registered'",
        (event_id, user["employer_id"]))}
    regs = conn.execute(
        "SELECT * FROM talent_registration WHERE event_id=?"
        " AND status='registered'", (event_id,)).fetchall()
    if not all:
        regs = [r for r in regs if r["id"] in interested]
    cards = [_anon_card(conn, ev, r, ee, user["employer_id"], interested)
             for r in regs]
    cards.sort(key=lambda c: hashlib.sha256(
        (user["employer_id"] + c["id"]).encode()).hexdigest())
    return {"cards": cards, "slots": ee["slots"],
            "interested_count": len(interested)}


@router.post("/employer/events/{event_id}/invites", status_code=201)
def invite(event_id: str, payload: EventInviteIn,
           conn: sqlite3.Connection = Depends(get_conn),
           user=Depends(current_user)):
    _employer(user)
    ev = _get_event(conn, event_id)
    ee = _ee(conn, event_id, user["employer_id"])
    if not ee:
        raise HTTPException(404, "Join the event first.")
    reg = conn.execute(
        "SELECT * FROM talent_registration WHERE id=? AND event_id=?"
        " AND status='registered'",
        (payload.registration_id, event_id)).fetchone()
    if not reg:
        raise HTTPException(404, "No such talent card.")
    if not conn.execute(
            "SELECT 1 FROM event_invite WHERE event_id=? AND employer_id=?"
            " AND registration_id=?",
            (event_id, user["employer_id"], reg["id"])).fetchone():
        used = conn.execute(
            "SELECT COUNT(*) c FROM event_invite WHERE event_id=?"
            " AND employer_id=?", (event_id, user["employer_id"])).fetchone()["c"]
        if used >= ee["slots"]:
            raise HTTPException(409, "All your meeting places are used. "
                                     "Raise the number of places or choose "
                                     "who matters most.")
        conn.execute(
            "INSERT INTO event_invite (event_id,employer_id,registration_id,"
            "created_at) VALUES (?,?,?,?)",
            (event_id, user["employer_id"], reg["id"],
             datetime.now(timezone.utc).isoformat(timespec="seconds")))
    meeting = book_if_mutual(conn, event_id, user["employer_id"],
                             reg["user_id"])
    db_mod.audit(conn, user["id"], "event_invite",
                 f"{event_id}:{reg['id']}")
    conn.commit()
    return {"meeting": meeting,
            "invites_used": conn.execute(
                "SELECT COUNT(*) c FROM event_invite WHERE event_id=?"
                " AND employer_id=?",
                (event_id, user["employer_id"])).fetchone()["c"]}


@router.get("/employer/events/{event_id}")
def employer_workspace(event_id: str,
                       conn: sqlite3.Connection = Depends(get_conn),
                       user=Depends(current_user)):
    _employer(user)
    ev = _get_event(conn, event_id)
    ee = _ee(conn, event_id, user["employer_id"])
    if not ee:
        return {"event": _event_out(ev, conn), "joined": False}
    invites_used = conn.execute(
        "SELECT COUNT(*) c FROM event_invite WHERE event_id=?"
        " AND employer_id=?", (event_id, user["employer_id"])).fetchone()["c"]
    meetings = [dict(r) for r in conn.execute(
        "SELECT m.id,m.starts_at,m.status FROM event_meeting m"
        " WHERE m.event_id=? AND m.employer_id=? AND m.status != 'cancelled'"
        " ORDER BY m.starts_at", (event_id, user["employer_id"]))]
    talks = []
    for tr in conn.execute(
            "SELECT t.id,t.status,t.outcome,t.employer_note,t.talked_at,"
            " t.meeting_id, u.name person_name FROM event_talk t"
            " LEFT JOIN user u ON u.id=t.user_id"
            " WHERE t.event_id=? AND t.employer_id=? ORDER BY t.talked_at",
            (event_id, user["employer_id"])):
        d = dict(tr)
        d["days_waiting"] = (
            _today() - date.fromisoformat(d["talked_at"][:10])).days
        talks.append(d)
    return {"event": _event_out(ev, conn), "joined": True,
            "booth": ee["booth"], "slots": ee["slots"],
            "formats": json.loads(ee["formats"] or "[]"),
            "need": _need_out(ee), "invites_used": invites_used,
            "meetings": meetings, "talks": talks}


# --- organizer (advisor) ---------------------------------------------------------

@router.get("/advisor/events/{event_id}")
def organizer_board(event_id: str,
                    conn: sqlite3.Connection = Depends(get_conn),
                    user=Depends(current_user)):
    _advisor(user)
    ev = _get_event(conn, event_id)
    today = _today()
    deadline = (date.fromisoformat(ev["need_deadline"])
                if ev["need_deadline"] else None)
    employers = []
    for ee in conn.execute(
            "SELECT ee.*, e.name, e.contact_name, e.contact_email,"
            " e.contact_phone FROM employer_event ee"
            " JOIN employer e ON e.id=ee.employer_id"
            " WHERE ee.event_id=? ORDER BY e.name", (event_id,)):
        if ee["need_card"]:
            submitted = date.fromisoformat(ee["need_submitted_at"]) \
                if ee["need_submitted_at"] else None
            need_status = "late" if deadline and submitted and \
                submitted > deadline else "on_time"
        else:
            need_status = "missing"
        invites = conn.execute(
            "SELECT COUNT(*) c FROM event_invite WHERE event_id=?"
            " AND employer_id=?", (event_id, ee["employer_id"])).fetchone()["c"]
        meetings = conn.execute(
            "SELECT COUNT(*) c FROM event_meeting WHERE event_id=?"
            " AND employer_id=? AND status != 'cancelled'",
            (event_id, ee["employer_id"])).fetchone()["c"]
        employers.append({
            "employer_id": ee["employer_id"], "name": ee["name"],
            "contact_name": ee["contact_name"],
            "contact_email": ee["contact_email"],
            "contact_phone": ee["contact_phone"],
            "booth": ee["booth"], "slots": ee["slots"],
            "formats": json.loads(ee["formats"] or "[]"),
            "need_status": need_status,
            "need_submitted_at": ee["need_submitted_at"],
            "need_by": ee["need_by"],
            "days_to_deadline": (deadline - today).days
            if deadline else None,
            "reminders_sent": ee["reminders_sent"],
            "invites_used": invites, "meetings": meetings})
    groups = {g["id"]: 0 for g in json.loads(ev["time_groups"] or "[]")}
    waitlist = 0
    for r in conn.execute(
            "SELECT time_group,status,COUNT(*) c FROM talent_registration"
            " WHERE event_id=? AND status != 'cancelled' GROUP BY time_group,"
            " status", (event_id,)):
        if r["status"] == "waitlist":
            waitlist += r["c"]
        elif r["time_group"] in groups:
            groups[r["time_group"]] += r["c"]
    mutual = conn.execute(
        "SELECT COUNT(*) c FROM event_invite i JOIN talent_registration tr"
        " ON tr.id=i.registration_id JOIN event_plan p"
        " ON p.event_id=i.event_id AND p.employer_id=i.employer_id"
        " AND p.user_id=tr.user_id WHERE i.event_id=?", (event_id,)
        ).fetchone()["c"]
    meetings = conn.execute(
        "SELECT COUNT(*) c FROM event_meeting WHERE event_id=?"
        " AND status != 'cancelled'", (event_id,)).fetchone()["c"]
    return {"event": _event_out(ev, conn), "employers": employers,
            "talent": {"by_time_group": groups, "waitlist": waitlist,
                       "mutual_matches": mutual, "meetings": meetings}}


@router.post("/advisor/events/{event_id}/remind")
def remind_employer(event_id: str, payload: dict,
                    conn: sqlite3.Connection = Depends(get_conn),
                    user=Depends(current_user)):
    """Simulated reminder: counter + timestamp + audit, nothing is sent."""
    _advisor(user)
    _get_event(conn, event_id)
    employer_id = (payload or {}).get("employer_id")
    ee = _ee(conn, event_id, employer_id)
    if not ee:
        raise HTTPException(404, "That employer is not at this event.")
    conn.execute(
        "UPDATE employer_event SET reminders_sent=reminders_sent+1,"
        " last_reminder_at=? WHERE event_id=? AND employer_id=?",
        (datetime.now(timezone.utc).isoformat(timespec="seconds"),
         event_id, employer_id))
    db_mod.audit(conn, user["id"], "event_reminder",
                 f"{event_id}:{employer_id}")
    conn.commit()
    return {"reminders_sent": ee["reminders_sent"] + 1}


@router.put("/advisor/events/{event_id}/need")
def advisor_submit_need(event_id: str, payload: OrgNeedIn,
                        conn: sqlite3.Connection = Depends(get_conn),
                        user=Depends(current_user)):
    """Advisor fills a need card with the employer by phone — marked
    'Written with an Employment Espoo advisor' on the public card."""
    _advisor(user)
    _get_event(conn, event_id)
    ee = _ee(conn, event_id, payload.employer_id)
    if not ee:
        raise HTTPException(404, "That employer is not at this event.")
    card = payload.card.model_dump(exclude_none=True)
    _check_need_card(card)
    conn.execute(
        "UPDATE employer_event SET need_card=?, need_submitted_at=?,"
        " need_by='advisor' WHERE event_id=? AND employer_id=?",
        (json.dumps(card, ensure_ascii=False),
         date.today().isoformat(), event_id, payload.employer_id))
    db_mod.audit(conn, user["id"], "event_need",
                 f"{event_id}:{payload.employer_id}:advisor")
    conn.commit()
    return {"ok": True, "need_by": "advisor"}


# --- On the day (v10) ------------------------------------------------------------

@router.put("/events/{event_id}/queue/{employer_id}", status_code=201)
def join_queue(event_id: str, employer_id: str,
               conn: sqlite3.Connection = Depends(get_conn),
               user=Depends(current_user)):
    """Join the walk-in queue at one booth. One position per person."""
    _resident(user)
    ev = _get_event(conn, event_id)
    if not _ee(conn, event_id, employer_id):
        raise HTTPException(404, "No such booth.")
    reg = _registration(conn, event_id, user["id"])
    if not reg or reg["status"] != "registered":
        raise HTTPException(409, "Register for the event first.")
    row = conn.execute(
        "SELECT status FROM event_queue WHERE event_id=? AND employer_id=?"
        " AND user_id=?", (event_id, employer_id, user["id"])).fetchone()
    if row and row["status"] in ("waiting", "called"):
        raise HTTPException(409, "You are already in this queue.")
    if row:
        conn.execute(
            "UPDATE event_queue SET status='waiting',"
            " joined_at=datetime('now') WHERE event_id=? AND"
            " employer_id=? AND user_id=?",
            (event_id, employer_id, user["id"]))
    else:
        conn.execute(
            "INSERT INTO event_queue (event_id,employer_id,user_id)"
            " VALUES (?,?,?)", (event_id, employer_id, user["id"]))
    db_mod.audit(conn, user["id"], "event_queue_join",
                 f"{event_id}:{employer_id}")
    conn.commit()
    return {"ok": True}


@router.delete("/events/{event_id}/queue/{employer_id}")
def leave_queue(event_id: str, employer_id: str,
                conn: sqlite3.Connection = Depends(get_conn),
                user=Depends(current_user)):
    _resident(user)
    conn.execute(
        "UPDATE event_queue SET status='left' WHERE event_id=?"
        " AND employer_id=? AND user_id=?",
        (event_id, employer_id, user["id"]))
    conn.commit()
    return {"ok": True}


def _queue_list(conn, event_id, employer_id):
    return [dict(r) for r in conn.execute(
        "SELECT q.user_id, q.status, q.joined_at,"
        " tr.id registration_id FROM event_queue q"
        " JOIN talent_registration tr"
        " ON tr.event_id=q.event_id AND tr.user_id=q.user_id"
        " WHERE q.event_id=? AND q.employer_id=? AND q.status='waiting'"
        " ORDER BY q.joined_at", (event_id, employer_id))]


def _next_free_slot(conn, ev, employer_id, user_id, entry="00:00"):
    """Earliest slot start free for both sides, at/after entry."""
    hhmm = lambda iso: iso.split("T")[1][:5]
    busy_p = {hhmm(r["starts_at"]) for r in conn.execute(
        "SELECT starts_at FROM event_meeting WHERE event_id=? AND user_id=?"
        " AND status != 'cancelled'", (ev["id"], user_id))}
    busy_e = {hhmm(r["starts_at"]) for r in conn.execute(
        "SELECT starts_at FROM event_meeting WHERE event_id=? AND"
        " employer_id=? AND status != 'cancelled'",
        (ev["id"], employer_id))}
    for slot in _slot_starts(ev):
        if slot < entry or slot in busy_p or slot in busy_e:
            continue
        return slot
    return None


@router.get("/employer/events/{event_id}/day")
def employer_day(event_id: str,
                 conn: sqlite3.Connection = Depends(get_conn),
                 user=Depends(current_user)):
    """Booth view: meetings in order, the next person's anonymous card,
    the walk-in queue."""
    _employer(user)
    ev = _get_event(conn, event_id)
    ee = _ee(conn, event_id, user["employer_id"])
    if not ee:
        raise HTTPException(404, "Join the event first.")
    meetings = [dict(r) for r in conn.execute(
        "SELECT m.* FROM event_meeting m"
        " WHERE m.event_id=? AND m.employer_id=?"
        " ORDER BY m.starts_at", (event_id, user["employer_id"]))]
    interested = {r["registration_id"] for r in conn.execute(
        "SELECT tr.id AS registration_id FROM event_plan p"
        " JOIN talent_registration tr"
        " ON tr.event_id=p.event_id AND tr.user_id=p.user_id"
        " WHERE p.event_id=? AND p.employer_id=?",
        (event_id, user["employer_id"]))}
    next_card = None
    for m in meetings:
        if m["status"] == "booked":
            reg = conn.execute(
                "SELECT * FROM talent_registration WHERE id=?",
                (m["registration_id"],)).fetchone()
            next_card = _anon_card(conn, ev, reg, ee,
                                   user["employer_id"], interested)
            next_card["meeting_id"] = m["id"]
            break
    return {"event": _event_out(ev, conn), "booth": ee["booth"],
            "meetings": meetings, "next_card": next_card,
            "queue": _queue_list(conn, event_id, user["employer_id"])}


@router.post("/employer/events/{event_id}/reveal")
def reveal_visitor(event_id: str, payload: VisitorCodeIn,
                   conn: sqlite3.Connection = Depends(get_conn),
                   user=Depends(current_user)):
    """The visitor says their number; the name appears for that meeting."""
    _employer(user)
    vis = conn.execute(
        "SELECT v.user_id, u.name FROM event_visitor v JOIN user u"
        " ON u.id=v.user_id WHERE v.event_id=? AND v.code=?",
        (event_id, payload.code)).fetchone()
    if not vis:
        raise HTTPException(404, "No visitor has that number. "
                                 "Check the number and try again.")
    m = conn.execute(
        "SELECT id,starts_at,status FROM event_meeting WHERE event_id=?"
        " AND employer_id=? AND user_id=? AND status != 'cancelled'",
        (event_id, user["employer_id"], vis["user_id"])).fetchone()
    return {"name": vis["name"], "user_id": vis["user_id"],
            "meeting": dict(m) if m else None}


@router.post("/employer/events/{event_id}/meetings/{meeting_id}/talk",
             status_code=201)
def record_meeting_talk(event_id: str, meeting_id: str,
                        payload: MeetingTalkIn,
                        conn: sqlite3.Connection = Depends(get_conn),
                        user=Depends(current_user)):
    """After the talk: observed items (subset of the employer's own
    first_week list) + the answer. Note is required."""
    _employer(user)
    m = conn.execute(
        "SELECT * FROM event_meeting WHERE id=? AND event_id=?",
        (meeting_id, event_id)).fetchone()
    if not m or m["employer_id"] != user["employer_id"]:
        raise HTTPException(404, "Meeting not found.")
    if m["status"] != "booked":
        raise HTTPException(409, "This meeting is already closed.")
    ee = _ee(conn, event_id, user["employer_id"])
    card = json.loads(ee["need_card"]) if ee["need_card"] else {}
    first_week = card.get("first_week") or []
    if any(o not in first_week for o in payload.observed):
        raise HTTPException(422, "Observed items must come from your "
                                 "first-week list.")
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    old = conn.execute(
        "SELECT id FROM event_talk WHERE event_id=? AND user_id=?"
        " AND employer_id=?", (event_id, m["user_id"],
                              user["employer_id"])).fetchone()
    if old:
        talk_id = old["id"]
        conn.execute(
            "UPDATE event_talk SET status='answered', outcome=?,"
            " meeting_id=?, observed=?, employer_note=?,"
            " answered_at=? WHERE id=?",
            (payload.outcome, meeting_id,
             json.dumps(payload.observed, ensure_ascii=False),
             payload.employer_note, now, talk_id))
    else:
        talk_id = db_mod.new_id(conn, "et")
        conn.execute(
            "INSERT INTO event_talk (id,event_id,user_id,employer_id,"
            "status,outcome,meeting_id,observed,employer_note,talked_at,"
            "answered_at) VALUES (?,?,?,?,'answered',?,?,?,?,?,?)",
            (talk_id, event_id, m["user_id"], user["employer_id"],
             payload.outcome, meeting_id,
             json.dumps(payload.observed, ensure_ascii=False),
             payload.employer_note, now, now))
    conn.execute(
        "UPDATE event_meeting SET status='done' WHERE id=?",
        (meeting_id,))
    db_mod.audit(conn, user["id"], "event_talk", talk_id)
    conn.commit()
    return {"talk_id": talk_id}


@router.post("/employer/events/{event_id}/meetings/{meeting_id}/no-show")
def meeting_no_show(event_id: str, meeting_id: str,
                    conn: sqlite3.Connection = Depends(get_conn),
                    user=Depends(current_user)):
    _employer(user)
    m = conn.execute(
        "SELECT * FROM event_meeting WHERE id=? AND event_id=?",
        (meeting_id, event_id)).fetchone()
    if not m or m["employer_id"] != user["employer_id"]:
        raise HTTPException(404, "Meeting not found.")
    conn.execute("UPDATE event_meeting SET status='no_show' WHERE id=?",
                 (meeting_id,))
    conn.commit()
    return {"ok": True}


@router.post("/employer/events/{event_id}/queue/call-next")
def call_next(event_id: str,
              conn: sqlite3.Connection = Depends(get_conn),
              user=Depends(current_user)):
    _employer(user)
    first = conn.execute(
        "SELECT user_id FROM event_queue WHERE event_id=? AND employer_id=?"
        " AND status='waiting' ORDER BY joined_at LIMIT 1",
        (event_id, user["employer_id"])).fetchone()
    if not first:
        raise HTTPException(404, "The queue is empty.")
    conn.execute(
        "UPDATE event_queue SET status='called' WHERE event_id=?"
        " AND employer_id=? AND user_id=?",
        (event_id, user["employer_id"], first["user_id"]))
    db_mod.audit(conn, user["id"], "event_queue_call",
                 f"{event_id}:{first['user_id']}")
    conn.commit()
    return {"called": first["user_id"]}


# --- organizer on the day ---------------------------------------------------------

@router.get("/advisor/events/{event_id}/day")
def organizer_day(event_id: str,
                  conn: sqlite3.Connection = Depends(get_conn),
                  user=Depends(current_user)):
    _advisor(user)
    ev = _get_event(conn, event_id)
    booths = []
    for ee in conn.execute(
            "SELECT ee.*, e.name FROM employer_event ee JOIN employer e"
            " ON e.id=ee.employer_id WHERE ee.event_id=? ORDER BY ee.booth",
            (event_id,)):
        ms = [dict(r) for r in conn.execute(
            "SELECT starts_at,status FROM event_meeting WHERE event_id=?"
            " AND employer_id=? AND status != 'cancelled'"
            " ORDER BY starts_at", (event_id, ee["employer_id"]))]
        booked = [m for m in ms if m["status"] == "booked"]
        held_slots = {m["starts_at"].split("T")[1][:5] for m in ms}
        free = sum(1 for sl in _slot_starts(ev) if sl not in held_slots)
        queue = conn.execute(
            "SELECT COUNT(*) c FROM event_queue WHERE event_id=?"
            " AND employer_id=? AND status='waiting'",
            (event_id, ee["employer_id"])).fetchone()["c"]
        booths.append({"employer_id": ee["employer_id"], "name": ee["name"],
                       "booth": ee["booth"],
                       "now": booked[0]["starts_at"] if booked else None,
                       "next": booked[1]["starts_at"]
                       if len(booked) > 1 else None,
                       "done": sum(1 for m in ms if m["status"] == "done"),
                       "no_show": sum(1 for m in ms
                                      if m["status"] == "no_show"),
                       "free_slots": free, "queue": queue})
    return {"event": _event_out(ev, conn), "booths": booths}


@router.post("/advisor/events/{event_id}/offer")
def offer_free_slot(event_id: str, payload: dict,
                    conn: sqlite3.Connection = Depends(get_conn),
                    user=Depends(current_user)):
    """Book the first person in the booth's walk-in queue into the next
    free slot. No double-booking on either side."""
    _advisor(user)
    ev = _get_event(conn, event_id)
    employer_id = payload.get("employer_id")
    first = conn.execute(
        "SELECT q.user_id, tr.time_group FROM event_queue q"
        " JOIN talent_registration tr"
        " ON tr.event_id=q.event_id AND tr.user_id=q.user_id"
        " WHERE q.event_id=? AND q.employer_id=? AND q.status='waiting'"
        " ORDER BY q.joined_at LIMIT 1",
        (event_id, employer_id)).fetchone()
    if not first:
        raise HTTPException(404, "The queue is empty.")
    groups = {g["id"]: g for g in json.loads(ev["time_groups"] or "[]")}
    entry = (groups.get(first["time_group"]) or {}).get("entry", "00:00")
    slot = _next_free_slot(conn, ev, employer_id, first["user_id"], entry)
    if not slot:
        raise HTTPException(409, "No free slot for this person.")
    reg = conn.execute(
        "SELECT id FROM talent_registration WHERE event_id=? AND user_id=?",
        (event_id, first["user_id"])).fetchone()
    mid = db_mod.new_id(conn, "mt")
    conn.execute(
        "INSERT INTO event_meeting (id,event_id,employer_id,user_id,"
        "registration_id,starts_at,status)"
        " VALUES (?,?,?,?,?,?,'booked')",
        (mid, event_id, employer_id, first["user_id"], reg["id"],
         f"{ev['date']}T{slot}:00"))
    conn.execute(
        "UPDATE event_queue SET status='called' WHERE event_id=?"
        " AND employer_id=? AND user_id=?",
        (event_id, employer_id, first["user_id"]))
    db_mod.audit(conn, user["id"], "event_offer",
                 f"{mid}:{employer_id}:{first['user_id']}")
    conn.commit()
    return {"meeting": {"id": mid, "starts_at": f"{ev['date']}T{slot}:00",
                        "status": "booked"}}


# --- After the event --------------------------------------------------------------

@router.get("/advisor/events/{event_id}/report")
def organizer_report(event_id: str,
                     conn: sqlite3.Connection = Depends(get_conn),
                     user=Depends(current_user)):
    """Per-booth stats + need-card punctuality + 7-day answers + the
    fairness panel (by card_language, groups < 10 get no rates)."""
    _advisor(user)
    ev = _get_event(conn, event_id)
    deadline = (date.fromisoformat(ev["need_deadline"])
                if ev["need_deadline"] else None)
    booths = []
    on_time = late = missing = 0
    for ee in conn.execute(
            "SELECT ee.*, e.name FROM employer_event ee JOIN employer e"
            " ON e.id=ee.employer_id WHERE ee.event_id=? ORDER BY ee.booth",
            (event_id,)):
        ms = conn.execute(
            "SELECT status,COUNT(*) c FROM event_meeting WHERE event_id=?"
            " AND employer_id=? AND status != 'cancelled'"
            " GROUP BY status", (event_id, ee["employer_id"])).fetchall()
        st = {r["status"]: r["c"] for r in ms}
        next_steps = conn.execute(
            "SELECT COUNT(*) c FROM event_talk WHERE event_id=?"
            " AND employer_id=? AND outcome='next_step'",
            (event_id, ee["employer_id"])).fetchone()["c"]
        if ee["need_card"]:
            sub = (date.fromisoformat(ee["need_submitted_at"])
                   if ee["need_submitted_at"] else None)
            if deadline and sub and sub > deadline:
                late += 1
            else:
                on_time += 1
        else:
            missing += 1
        booths.append({"employer_id": ee["employer_id"], "name": ee["name"],
                       "booth": ee["booth"], "booked": st.get("booked", 0),
                       "held": st.get("done", 0),
                       "no_show": st.get("no_show", 0),
                       "next_step": next_steps})
    total_cards = on_time + late
    cards_pct = (round(100 * on_time / total_cards)
                 if total_cards else None)

    talks = conn.execute(
        "SELECT talked_at,answered_at FROM event_talk WHERE event_id=?",
        (event_id,)).fetchall()
    answered7 = 0
    for t in talks:
        if t["answered_at"]:
            d0 = date.fromisoformat(t["talked_at"][:10])
            d1 = date.fromisoformat(t["answered_at"][:10])
            if (d1 - d0).days <= 7:
                answered7 += 1
    ans7_pct = (round(100 * answered7 / len(talks)) if talks else None)

    # fairness: registered -> chose -> invited -> met -> next step
    groups = {}
    for r in conn.execute(
            "SELECT tr.id rid, tr.user_id uid, tr.card_language lang"
            " FROM talent_registration tr WHERE tr.event_id=?"
            " AND tr.status != 'cancelled'", (event_id,)):
        g = groups.setdefault(r["lang"], {
            "card_language": r["lang"], "registered": 0,
            "chose": 0, "invited": 0, "met": 0, "next_step": 0})
        g["registered"] += 1
        g["chose"] += 1 if conn.execute(
            "SELECT 1 FROM event_plan WHERE event_id=? AND user_id=?"
            " LIMIT 1", (event_id, r["uid"])).fetchone() else 0
        g["invited"] += 1 if conn.execute(
            "SELECT 1 FROM event_invite WHERE event_id=?"
            " AND registration_id=? LIMIT 1",
            (event_id, r["rid"])).fetchone() else 0
        g["met"] += 1 if conn.execute(
            "SELECT 1 FROM event_meeting WHERE event_id=? AND user_id=?"
            " AND status IN ('booked','done') LIMIT 1",
            (event_id, r["uid"])).fetchone() else 0
        g["next_step"] += 1 if conn.execute(
            "SELECT 1 FROM event_talk WHERE event_id=? AND user_id=?"
            " AND outcome='next_step' LIMIT 1",
            (event_id, r["uid"])).fetchone() else 0
    fairness = []
    for g in sorted(groups.values(), key=lambda x: -x["registered"]):
        if g["registered"] >= 10:
            base = g["registered"]
            g["rates"] = {k: round(100 * g[k] / base)
                          for k in ("chose", "invited", "met", "next_step")}
        else:
            g["rates"] = None               # fewer than 10: no rates
        fairness.append(g)
    return {"event": _event_out(ev, conn), "booths": booths,
            "need_cards_on_time_pct": cards_pct,
            "answers_in_7d_pct": ans7_pct, "fairness": fairness}
