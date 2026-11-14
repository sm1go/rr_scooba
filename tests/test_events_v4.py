"""Spec v9 event mode: multi-event listing, need cards + wording check,
talent registration, mutual-interest booking, anonymous employer cards,
organizer board, AI card helper. No test calls the network."""

from __future__ import annotations

import json
from datetime import date, timedelta

import pytest

from app.api import db as db_mod

pytestmark = pytest.mark.usefixtures("client")

E1, E2 = "ev-2027-03", "ev-2026-11"


def _card(**kw):
    c = {"looking_for": "kitchen or cleaning work",
         "done": [{"text": "Ran the till alone on Saturdays",
                   "own_words": "Ran the till alone on Saturdays"}],
         "district": "", "availability": ["mon-morning"]}
    c.update(kw)
    return c


def _reg(client, email, group="A", **kw):
    r = client.post("/api/auth/register", json={
        "role": "resident", "name": "Uusi Ihminen",
        "email": email, "password": "password9"})
    assert r.status_code == 201, r.text
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    r = client.post(f"/api/events/{E1}/register", headers=h,
                    json={"time_group": group, "card_language": "en",
                          "card": _card(**kw)})
    assert r.status_code == 201, r.text
    return h, r.json()["registration"]


def _need(**kw):
    n = {"first_week": ["Learn the till with a buddy"],
         "must_haves": [{"text": "You can stand for a 4-hour shift",
                         "why": "lunch service is standing work"}],
         "will_teach": ["The till system"], "languages": [],
         "job_ids": []}
    n.update(kw)
    return n


# --- listing & phases -----------------------------------------------------------

def test_events_lists_both_with_phase(client):
    r = client.get("/api/events")
    assert r.status_code == 200
    ids = {e["id"]: e for e in r.json()["events"]}
    assert E1 in ids and E2 in ids
    assert ids[E1]["phase"] in ("registration", "needs_published",
                                "today", "finished")
    assert ids[E2]["format"] == "treffit"


def test_event_detail_public_anonymous(client):
    r = client.get(f"/api/events/{E1}")
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == E1 and len(d["employers"]) == 12
    assert d["needs_published"] is False           # publish_date is in the future
    assert all(e["need"] is None for e in d["employers"])


def test_needs_hidden_before_publish_then_open(client, monkeypatch):
    from app.api.routers import events as ev_mod
    r = client.get(f"/api/events/{E1}/needs")
    assert r.status_code == 403
    future = date.fromisoformat("2027-03-10")
    monkeypatch.setattr(ev_mod, "_today", lambda: future)
    r = client.get(f"/api/events/{E1}/needs")
    assert r.status_code == 200
    assert len(r.json()["cards"]) == 9              # 9 submitted need cards


# --- need card submission + wording check ----------------------------------------

def test_employer_submit_need_valid(client, sanna):
    r = client.put(f"/api/employer/events/{E1}/need", headers=sanna,
                   json=_need())
    assert r.status_code == 200, r.text
    assert r.json()["need"]["card"]["first_week"]
    assert r.json()["need"]["submitted_at"]


def test_employer_need_blocked_wording(client, sanna):
    r = client.put(f"/api/employer/events/{E1}/need", headers=sanna,
                   json=_need(must_haves=[
                       {"text": "You are a native Finnish speaker",
                        "why": "customers speak Finnish"}]))
    assert r.status_code == 422


def test_employer_need_max_three_musts(client, sanna):
    mh = [{"text": f"Requirement {i}", "why": "real reason"}
          for i in range(4)]
    r = client.put(f"/api/employer/events/{E1}/need", headers=sanna,
                   json=_need(must_haves=mh))
    assert r.status_code == 422


def test_advisor_can_write_card_for_employer(client, advisor):
    r = client.put(f"/api/advisor/events/{E1}/need", headers=advisor,
                   json={"employer_id": "emp-espoolive", "card": _need()})
    assert r.status_code == 200, r.text
    assert r.json()["need_by"] == "advisor"
    ws = client.get(f"/api/advisor/events/{E1}", headers=advisor).json()
    row = next(e for e in ws["employers"]
               if e["employer_id"] == "emp-espoolive")
    assert row["need_by"] == "advisor" and row["need_status"] != "missing"


def test_resident_cannot_use_organizer_endpoints(client, aino):
    assert client.get(f"/api/advisor/events/{E1}", headers=aino
                      ).status_code == 403
    assert client.post(f"/api/advisor/events/{E1}/remind", headers=aino,
                       json={"employer_id": "emp-hymy"}).status_code == 403
    assert client.get(f"/api/employer/events/{E1}/cards",
                      headers=aino).status_code == 403


# --- registration -----------------------------------------------------------------

def test_second_registration_conflict(client, aino):
    r = client.post(f"/api/events/{E1}/register", headers=aino,
                    json={"time_group": "A", "card": _card()})
    assert r.status_code == 409


def test_capacity_full_waitlists(client):
    # shrink capacity below current registrations in the test DB
    conn = db_mod.connect()
    conn.execute("UPDATE event SET capacity=10 WHERE id=?", (E1,))
    conn.commit(); conn.close()
    h, reg = _reg(client, "cap-test@example.com")
    r = client.get(f"/api/events/{E1}/my", headers=h).json()
    assert r["registration"]["status"] == "waitlist"


def test_interest_limit_five(client):
    h, reg = _reg(client, "int-limit@example.com")
    emps = [e["employer_id"] for e in
            client.get(f"/api/events/{E1}").json()["employers"]]
    for eid in emps[:5]:
        r = client.put(f"/api/events/{E1}/interests/{eid}", headers=h,
                       json={"meets": [], "language_levels": {}})
        assert r.status_code in (200, 201), r.text
    r = client.put(f"/api/events/{E1}/interests/{emps[5]}", headers=h,
                   json={"meets": [], "language_levels": {}})
    assert r.status_code == 409


def test_invite_limit_equals_slots(client, sanna):
    # sanna has 8 slots and 5 seeded invites -> three more fit, fourth fails
    regs = []
    for i in range(4):
        _, reg = _reg(client, f"invite-cap{i}@example.com")
        regs.append(reg["id"])
    for rid in regs[:3]:
        r = client.post(f"/api/employer/events/{E1}/invites", headers=sanna,
                        json={"registration_id": rid})
        assert r.status_code in (200, 201), r.text
    r = client.post(f"/api/employer/events/{E1}/invites", headers=sanna,
                    json={"registration_id": regs[3]})
    assert r.status_code == 409


# --- mutual booking ---------------------------------------------------------------

def test_mutual_interest_books_meetings_no_overlap(client):
    # three people in the same time group all choose employer espoolive
    people = []
    for i in range(3):
        h, reg = _reg(client, f"mutual{i}@example.com", group="A")
        r = client.put(f"/api/events/{E1}/interests/emp-espoolive",
                       headers=h, json={"meets": [], "language_levels": {}})
        assert r.status_code in (200, 201), r.text
        people.append((h, reg["id"]))
    # employer needs an event row: join via advisor? espoolive is seeded
    # in E1 already; invites are sent by that employer. There is no seeded
    # espoolive login, so use the DB to send invites through the booking fn.
    conn = db_mod.connect()
    from app.api.routers import events as ev_mod
    starts = []
    for h, rid in people:
        conn.execute(
            "INSERT INTO event_invite (event_id,employer_id,"
            " registration_id,created_at) VALUES (?,?,?,?)",
            (E1, "emp-espoolive", rid, date.today().isoformat()))
        uid = conn.execute(
            "SELECT user_id FROM talent_registration WHERE id=?",
            (rid,)).fetchone()["user_id"]
        m = ev_mod.book_if_mutual(conn, E1, "emp-espoolive", uid)
        assert m and m["status"] == "booked"
        starts.append(m["starts_at"])
    conn.commit()
    # exactly one meeting per person, at or after the 14:30 group entry,
    # and no two meetings share a start time
    times = sorted(s.split("T")[1] for s in starts)
    assert len(set(times)) == 3
    assert all(t >= "14:30" for t in times)
    got = {r["user_id"] for r in conn.execute(
        "SELECT tr.user_id FROM event_meeting m"
        " JOIN talent_registration tr ON tr.id=m.registration_id"
        " WHERE m.event_id=? AND m.employer_id='emp-espoolive'",
        (E1,))}
    assert len(got) == 3
    conn.close()


def test_one_sided_interest_no_meeting(client):
    h, reg = _reg(client, "oneside@example.com")
    r = client.put(f"/api/events/{E1}/interests/emp-hymy", headers=h,
                   json={"meets": [], "language_levels": {}})
    assert r.status_code in (200, 201)
    my = client.get(f"/api/events/{E1}/my", headers=h).json()
    assert not any(m["employer_id"] == "emp-hymy" for m in my["meetings"])


# --- anonymous employer cards ------------------------------------------------------

def test_anonymous_cards_leak_nothing(client, sanna):
    r = client.get(f"/api/employer/events/{E1}/cards?all=1", headers=sanna)
    assert r.status_code == 200
    raw = json.dumps(r.json())
    for secret in ("aino@example.com", "pekka@example.com",
                   "talent01@example.com", "u-aino", "u-pekka",
                   "@example.com"):
        assert secret not in raw
    card = r.json()["cards"][0]
    for k in ("name", "user_id", "email", "phone"):
        assert k not in card
    assert card["id"].startswith("tr-")


def test_anonymous_cards_order_stable_and_per_employer(client, sanna):
    a = [c["id"] for c in client.get(
        f"/api/employer/events/{E1}/cards?all=1", headers=sanna
    ).json()["cards"]]
    b = [c["id"] for c in client.get(
        f"/api/employer/events/{E1}/cards?all=1", headers=sanna
    ).json()["cards"]]
    assert a == b
    # a different employer would hash a different order — verify directly
    import hashlib
    def order_for(emp):
        return sorted(a, key=lambda rid: hashlib.sha256(
            (emp + rid).encode()).hexdigest())
    assert order_for("emp-cafe-koivu") == a
    assert order_for("emp-hymy") != a


def test_employer_cards_default_only_interested(client, sanna):
    r = client.get(f"/api/employer/events/{E1}/cards", headers=sanna)
    assert all(c["interested"] for c in r.json()["cards"])


# --- organizer board --------------------------------------------------------------

def test_organizer_board_and_reminder(client, advisor):
    r = client.get(f"/api/advisor/events/{E1}", headers=advisor)
    assert r.status_code == 200
    d = r.json()
    assert len(d["employers"]) == 12
    statuses = {e["employer_id"]: e["need_status"] for e in d["employers"]}
    assert "missing" in statuses.values() and "late" in statuses.values()
    assert "on_time" in statuses.values()
    before = next(e for e in d["employers"]
                  if e["employer_id"] == "emp-hymy")["reminders_sent"]
    r = client.post(f"/api/advisor/events/{E1}/remind", headers=advisor,
                    json={"employer_id": "emp-hymy"})
    assert r.status_code == 200
    assert r.json()["reminders_sent"] == before + 1
    assert d["talent"]["meetings"] == 39


# --- AI card helper ----------------------------------------------------------------

class _FakeLLM:
    def __init__(self, reply):
        self.reply = reply
    def chat(self, messages):
        return self.reply


def test_ai_event_card_returns_lines(client, aino, monkeypatch):
    from app.api import llm, settings
    monkeypatch.setattr(settings, "ai_enabled", lambda: True)
    llm.set_client(_FakeLLM({"lines": [
        "Ran the till alone on Saturdays at a kiosk"]}))
    try:
        r = client.post("/api/ai/event-card", headers=aino,
                        json={"items": ["i ran the till alone on saturdays at a kiosk"]})
        assert r.status_code == 200
        assert r.json()["lines"] == [
            "Ran the till alone on Saturdays at a kiosk"]
    finally:
        llm.set_client(None)


def test_ai_event_card_off_is_disabled(client, aino, monkeypatch):
    from app.api import settings
    monkeypatch.setattr(settings, "ai_enabled", lambda: False)
    r = client.post("/api/ai/event-card", headers=aino,
                    json={"items": ["hello"]})
    assert r.status_code in (403, 503)


# --- §8 simplify: meeting in responses, demo flag, seeded demo conditions ----

def test_interest_response_includes_meeting_key(client):
    h, _ = _reg(client, "meeting-key@example.com")
    r = client.put(f"/api/events/{E1}/interests/emp-hymy", headers=h,
                   json={"meets": [], "language_levels": {}})
    assert r.status_code == 201
    assert "meeting" in r.json()          # None while not mutual


def test_invite_response_includes_meeting_key(client, sanna):
    _, reg = _reg(client, "invite-key@example.com")
    r = client.post(f"/api/employer/events/{E1}/invites", headers=sanna,
                    json={"registration_id": reg["id"]})
    assert r.status_code == 201
    body = r.json()
    assert "meeting" in body and "invites_used" in body


def test_invite_then_interest_books_and_returns_meeting(client, sanna):
    h, reg = _reg(client, "mutual-key@example.com")
    r = client.post(f"/api/employer/events/{E1}/invites", headers=sanna,
                    json={"registration_id": reg["id"]})
    assert r.json()["meeting"] is None    # one-sided so far
    emp = db_mod.connect().execute(
        "SELECT employer_id FROM user WHERE id='u-sanna'"
    ).fetchone()["employer_id"]
    r = client.put(f"/api/events/{E1}/interests/{emp}", headers=h,
                   json={"meets": [], "language_levels": {}})
    assert r.status_code == 201
    m = r.json()["meeting"]
    assert m and m["status"] == "booked" and m["starts_at"]


def test_config_has_demo_flag(client):
    body = client.get("/api/config").json()
    assert isinstance(body.get("demo"), bool)


def test_seed_aino_has_unchosen_inviter_and_cards(client, aino):
    """§8 demo seed: Aino can trigger a match and has ≥4 cards to swipe."""
    conn = db_mod.connect()
    chosen = {r["employer_id"] for r in conn.execute(
        "SELECT employer_id FROM event_plan WHERE event_id=? AND user_id=?",
        (E1, "u-aino"))}
    invited = [r["employer_id"] for r in conn.execute(
        "SELECT i.employer_id FROM event_invite i"
        " JOIN talent_registration r ON r.id=i.registration_id"
        " WHERE i.event_id=? AND r.user_id=?", (E1, "u-aino"))]
    assert any(e not in chosen for e in invited)
    cards = [r["employer_id"] for r in conn.execute(
        "SELECT employer_id FROM employer_event WHERE event_id=?"
        " AND need_card IS NOT NULL", (E1,))]
    assert len([e for e in cards if e not in chosen]) >= 4


def test_seed_sanna_has_unchosen_fan_and_invites_left(client, sanna):
    """§8 demo seed: someone chose Sanna's booth and was not invited yet."""
    conn = db_mod.connect()
    emp = conn.execute("SELECT employer_id FROM user WHERE id='u-sanna'"
                      ).fetchone()["employer_id"]
    reg_by_user = {r["user_id"]: r["id"] for r in conn.execute(
        "SELECT id,user_id FROM talent_registration WHERE event_id=?"
        " AND status='registered'", (E1,))}
    fans = [r["user_id"] for r in conn.execute(
        "SELECT user_id FROM event_plan WHERE event_id=? AND employer_id=?",
        (E1, emp))]
    invited = {r["registration_id"] for r in conn.execute(
        "SELECT registration_id FROM event_invite WHERE event_id=?"
        " AND employer_id=?", (E1, emp))}
    assert any(reg_by_user.get(u) not in invited
               for u in fans if u in reg_by_user)
    slots = conn.execute("SELECT slots FROM employer_event WHERE event_id=?"
                        " AND employer_id=?", (E1, emp)).fetchone()["slots"]
    assert len(invited) < slots


def test_aino_choosing_seeded_inviter_returns_meeting(client, aino):
    """The seeded invite makes Aino's choice book a real meeting."""
    conn = db_mod.connect()
    chosen = {r["employer_id"] for r in conn.execute(
        "SELECT employer_id FROM event_plan WHERE event_id=? AND user_id=?",
        (E1, "u-aino"))}
    target = next(r["employer_id"] for r in conn.execute(
        "SELECT i.employer_id FROM event_invite i"
        " JOIN talent_registration r ON r.id=i.registration_id"
        " WHERE i.event_id=? AND r.user_id=?", (E1, "u-aino"))
        if r["employer_id"] not in chosen)
    r = client.put(f"/api/events/{E1}/interests/{target}", headers=aino,
                   json={"meets": [], "language_levels": {}})
    assert r.status_code == 201, r.text
    m = r.json()["meeting"]
    assert m and m["status"] == "booked" and m["starts_at"]
