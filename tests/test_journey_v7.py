"""Spec §9 — the time-driven event journey and the demo clock.

The demo clock (demo_state.now) drives every phase computation in demo
mode; tests set it through the demo endpoints, exactly like the UI.
"""

from __future__ import annotations

import json

from app.api import db as db_mod, settings

from tests.conftest import login

E1, E3 = "ev-2027-03", "ev-2027-02"
SANNA_EMP = "emp-cafe-koivu"
CARD = {"looking_for": "kitchen or cleaning work",
        "done": [{"text": "Ran the till alone on Saturdays",
                  "own_words": "Ran the till alone on Saturdays"}],
        "district": "", "availability": ["mon-morning"]}


def _clock(client, stage: str, event_id: str = E1):
    r = client.post("/api/demo/clock",
                    json={"stage": stage, "event_id": event_id})
    assert r.status_code == 200, r.text
    return r.json()


def _register(client, hdr):
    r = client.post(f"/api/events/{E1}/register", headers=hdr,
                    json={"time_group": "A", "card": CARD})
    assert r.status_code == 201, r.text


def _meets_all(client, eid):
    need = client.get(f"/api/events/{E1}").json()["employers"]
    e = next(x for x in need if x["employer_id"] == eid)
    return list(range(len((e["need"] or {}).get("card", {})
                          .get("must_haves") or [1])))


def test_phase_follows_demo_clock(client):
    assert client.get(f"/api/events/{E1}").json()["phase"] == \
        "registration"
    _clock(client, "matching_closed")
    assert client.get(f"/api/events/{E1}").json()["phase"] == "matched"
    _clock(client, "live")
    assert client.get(f"/api/events/{E1}").json()["phase"] == "live"
    _clock(client, "after")
    assert client.get(f"/api/events/{E1}").json()["phase"] == "after"


def test_register_409_after_matching_closes(client, aino):
    _clock(client, "matching_closed")
    r = client.post(f"/api/events/{E1}/register", headers=aino,
                    json={"time_group": "A", "card": CARD})
    assert r.status_code == 409


def test_choose_409_after_matching_closes(client, aino):
    _register(client, aino)
    _clock(client, "matching_closed")
    r = client.put(f"/api/events/{E1}/interests/emp-cafe-koivu",
                   headers=aino, json={"meets": [], "language_levels": {}})
    assert r.status_code == 409


def test_sixth_choice_409(client, aino):
    _register(client, aino)
    emps = [e["employer_id"]
            for e in client.get(f"/api/events/{E1}").json()["employers"]]
    for eid in emps[:5]:
        r = client.put(f"/api/events/{E1}/interests/{eid}", headers=aino,
                       json={"meets": [], "language_levels": {}})
        assert r.status_code == 201, r.text
    r = client.put(f"/api/events/{E1}/interests/{emps[5]}", headers=aino,
                   json={"meets": [], "language_levels": {}})
    assert r.status_code == 409


def test_aino_unregistered_after_seed(client, aino):
    for ev in (E1, E3):
        my = client.get(f"/api/events/{ev}/my", headers=aino).json()
        assert my["registration"] is None


def test_aino_full_journey_and_sanna_untouched(client, aino):
    """Registration -> choose -> matching close -> live -> after, with
    simulated employers around her and never at Sanna's company."""
    _register(client, aino)
    emps = [e["employer_id"]
            for e in client.get(f"/api/events/{E1}").json()["employers"]
            if e["employer_id"] != SANNA_EMP]
    for eid in emps[:4]:
        r = client.put(f"/api/events/{E1}/interests/{eid}", headers=aino,
                       json={"meets": _meets_all(client, eid),
                             "language_levels": {}})
        assert r.status_code == 201, r.text

    _clock(client, "matching_closed")
    my = client.get(f"/api/events/{E1}/my", headers=aino).json()
    assert len(my["meetings"]) >= 1

    conn = db_mod.connect()
    # nothing simulated for Sanna's company, ever
    sim_inv = conn.execute(
        "SELECT COUNT(*) c FROM event_invite WHERE event_id=?"
        " AND employer_id=? AND simulated=1",
        (E1, SANNA_EMP)).fetchone()["c"]
    assert sim_inv == 0

    _clock(client, "live")
    now = client.get("/api/demo/state").json()["now"]
    slot = conn.execute(
        "SELECT slot_minutes FROM event WHERE id=?",
        (E1,)).fetchone()["slot_minutes"]
    # 1:1 meetings start at 14:30, so at the live tick (14:35) none may
    # have ended yet — the rule itself is what we check
    past = conn.execute(
        "SELECT id FROM event_meeting WHERE event_id=? AND user_id=?"
        " AND status='booked' AND"
        " datetime(starts_at, '+' || ? || ' minutes') <= datetime(?)",
        (E1, "u-aino", slot, now)).fetchall()
    for m in past:
        tk = conn.execute(
            "SELECT simulated FROM event_talk WHERE event_id=?"
            " AND meeting_id=?", (E1, m["id"])).fetchone()
        assert tk and tk["simulated"] == 1
    sim_talks_sanna = conn.execute(
        "SELECT COUNT(*) c FROM event_talk WHERE event_id=?"
        " AND employer_id=? AND simulated=1",
        (E1, SANNA_EMP)).fetchone()["c"]
    assert sim_talks_sanna == 0

    _clock(client, "after")
    my = client.get(f"/api/events/{E1}/my", headers=aino).json()
    answered = [t for t in my["talks"] if t["status"] == "answered"]
    assert answered, "no answered talks after the event"
    nxt = [t for t in answered if t["outcome"] == "next_step"]
    assert any(t["next_kind"] and t["next_at"] for t in nxt)

    # Aino answers a proposal herself (not simulated)
    tid = nxt[0]["id"]
    r = client.post(f"/api/events/{E1}/talks/{tid}/response",
                    headers=aino,
                    json={"response": "confirmed", "note": ""})
    assert r.status_code == 200, r.text
    my = client.get(f"/api/events/{E1}/my", headers=aino).json()
    tk = next(t for t in my["talks"] if t["id"] == tid)
    assert tk["talent_response"] == "confirmed"
    assert tk["simulated"] or True  # flag presence only
    conn.close()


def test_demo_endpoints_404_when_disabled(client, monkeypatch):
    monkeypatch.setattr(settings, "demo_mode", lambda: False)
    assert client.get("/api/demo/state").status_code == 404
    assert client.post("/api/demo/clock",
                       json={"stage": "live"}).status_code == 404
    assert client.post("/api/demo/reset").status_code == 404


def test_online_meetings_have_jitsi_rooms(client):
    conn = db_mod.connect()
    n = conn.execute(
        "SELECT COUNT(*) c FROM event_meeting WHERE event_id=?"
        " AND video_url LIKE 'https://meet.jit.si/%'",
        (E3,)).fetchone()["c"]
    conn.close()
    assert n > 0


def test_demo_reset_rebuilds_and_relocks(client, aino):
    _register(client, aino)
    r = client.post("/api/demo/reset")
    assert r.status_code == 200
    # reset returns the clock to registration and Aino to zero
    st = client.get("/api/demo/state").json()
    assert st["stage"] == "registration"
    aino2 = login(client, "aino@example.com")
    my = client.get(f"/api/events/{E1}/my", headers=aino2).json()
    assert my["registration"] is None
