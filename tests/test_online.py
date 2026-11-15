"""Online event environment (spec §9.7): virtual booth Q&A, networking
lounge, live-stage progression and free slots for Aino's choices."""

from __future__ import annotations

from app.api import db as db_mod

from tests.conftest import login  # noqa: F401 (kept for parity)

E1 = "ev-2027-03"
E3 = "ev-2027-02"
BOOTH = "emp-lumo"          # seeded E3 booth with Q&A
CARD = {"done": [{"text": "I stocked shelves", "own_words": "I stocked shelves"}],
        "looking_for": "Part-time work in a shop",
        "district": "olari", "availability": ["mon-morning"]}


def _clock(client, stage: str, event_id: str):
    r = client.post("/api/demo/clock",
                    json={"stage": stage, "event_id": event_id})
    assert r.status_code == 200, r.text


def _register(client, hdr, event_id: str):
    r = client.post(f"/api/events/{event_id}/register", headers=hdr,
                    json={"time_group": "A", "card": CARD})
    assert r.status_code == 201, r.text


def _all_meets(client, hdr, event_id, eid):
    emps = client.get(f"/api/events/{event_id}", headers=hdr).json()["employers"]
    e = next(x for x in emps if x["employer_id"] == eid)
    return list(range(len((e["need"] or {}).get("card", {})
                          .get("must_haves") or [1])))


def _aino_e3_path(client, aino):
    """Register + choose 4 online employers + matching_closed -> meetings."""
    _clock(client, "registration", E3)
    _register(client, aino, E3)
    emps = [e["employer_id"] for e in
            client.get(f"/api/events/{E3}", headers=aino).json()["employers"]]
    for eid in emps[:4]:
        r = client.put(f"/api/events/{E3}/interests/{eid}", headers=aino,
                       json={"meets": _all_meets(client, aino, E3, eid),
                             "language_levels": {}})
        assert r.status_code == 201, r.text
    _clock(client, "matching_closed", E3)


# --- Q&A board ------------------------------------------------------------

def test_question_requires_registration(client, aino):
    """Aino is not registered at the online event after a reset."""
    _clock(client, "registration", E3)
    r = client.post(f"/api/events/{E3}/booths/{BOOTH}/questions",
                    headers=aino, json={"text": "Is it remote?"})
    assert r.status_code == 403


def test_question_limit_and_wording(client, pekka):
    """Pekka is a seeded E3 participant."""
    r = client.post(f"/api/events/{E3}/booths/{BOOTH}/questions",
                    headers=pekka, json={"text": "x" * 301})
    assert r.status_code == 422
    r = client.post(f"/api/events/{E3}/booths/{BOOTH}/questions",
                    headers=pekka,
                    json={"text": "Is this job only for young people?"})
    assert r.status_code == 422
    r = client.post(f"/api/events/{E3}/booths/{BOOTH}/questions",
                    headers=pekka,
                    json={"text": "What are the usual hours?"})
    assert r.status_code == 201, r.text


def test_answer_only_own_employer(client, sanna):
    """Sanna's employer is switched to an online booth for this check."""
    conn = db_mod.connect()
    conn.execute("UPDATE user SET employer_id=? WHERE id='u-sanna'",
                 (BOOTH,))
    conn.commit()
    qs = client.get(f"/api/events/{E3}/booths/{BOOTH}",
                    headers=sanna).json()["questions"]
    open_q = next(q for q in qs if not q["answer"])
    r = client.post(f"/api/events/{E3}/questions/{open_q['id']}/answer",
                    headers=sanna, json={"answer": "Both — you choose."})
    assert r.status_code == 200, r.text
    # ...but she cannot answer another employer's booth
    other = client.get(f"/api/events/{E3}/booths/emp-otava",
                       headers=sanna).json()["questions"]
    r = client.post(
        f"/api/events/{E3}/questions/{other[0]['id']}/answer",
        headers=sanna, json={"answer": "Hi"})
    assert r.status_code == 403


def test_board_hides_surnames_and_emails(client, pekka):
    board = client.get(f"/api/events/{E3}/booths/{BOOTH}",
                       headers=pekka).json()
    blob = str(board["questions"])
    for q in board["questions"]:
        assert " " not in q["asked_by"], "first name only"
        assert "@" not in q["asked_by"]
    assert "@" not in blob


def test_booth_anonymous_and_nonparticipant(client, sanna):
    r = client.get(f"/api/events/{E3}/booths/{BOOTH}")
    assert r.status_code in (401, 403)
    # Sanna's employer is not at the online event -> 403
    r = client.get(f"/api/events/{E3}/booths/{BOOTH}", headers=sanna)
    assert r.status_code == 403


# --- networking lounge ----------------------------------------------------

def test_lounge_connect_members_only(client, aino):
    conn = db_mod.connect()
    other = conn.execute(
        "SELECT user_id FROM lounge_member WHERE event_id=? LIMIT 1",
        (E3,)).fetchone()["user_id"]
    _clock(client, "registration", E3)
    _register(client, aino, E3)
    # not a lounge member yet -> 403
    r = client.post(f"/api/events/{E3}/lounge/connect/{other}",
                    headers=aino)
    assert r.status_code == 403
    # join, then connect twice -> idempotent 200
    r = client.put(f"/api/events/{E3}/lounge", headers=aino)
    assert r.status_code == 200 and r.json()["joined"]
    r = client.post(f"/api/events/{E3}/lounge/connect/{other}",
                    headers=aino)
    assert r.status_code == 200 and r.json()["connected"]
    r = client.post(f"/api/events/{E3}/lounge/connect/{other}",
                    headers=aino)
    assert r.status_code == 200
    # a non-member target fails too
    conn.execute("DELETE FROM lounge_member WHERE event_id=? AND user_id=?",
                 (E3, other))
    conn.commit()
    r = client.post(f"/api/events/{E3}/lounge/connect/{other}",
                    headers=aino)
    assert r.status_code == 403


def test_lounge_shows_first_names(client, pekka):
    data = client.get(f"/api/events/{E3}/lounge", headers=pekka).json()
    for m in data["members"]:
        assert " " not in m["first_name"]
        assert "@" not in m["first_name"]


# --- live stage progression + free slots ------------------------------------

def test_live_stage_done_and_upcoming_both_events(client, aino):
    """At the live tick each event has at least one finished talk and one
    upcoming meeting (E1 15:05, E3 11:35)."""
    # --- in-person E1
    _clock(client, "registration", E1)
    _register(client, aino, E1)
    emps = [e["employer_id"] for e in
            client.get(f"/api/events/{E1}", headers=aino).json()["employers"]
            if e["employer_id"] != "emp-cafe-koivu"]
    for eid in emps[:4]:
        client.put(f"/api/events/{E1}/interests/{eid}", headers=aino,
                   json={"meets": _all_meets(client, aino, E1, eid),
                         "language_levels": {}})
    _clock(client, "matching_closed", E1)
    _clock(client, "live", E1)
    conn = db_mod.connect()
    done = conn.execute(
        "SELECT COUNT(*) c FROM event_meeting WHERE event_id=?"
        " AND status='done'", (E1,)).fetchone()["c"]
    talks = conn.execute(
        "SELECT COUNT(*) c FROM event_talk WHERE event_id=?",
        (E1,)).fetchone()["c"]
    mine = client.get(f"/api/events/{E1}/my", headers=aino).json()
    up = [m for m in mine["meetings"] if m["status"] == "booked"]
    assert done >= 1 and talks >= 1, "no finished talk at the live tick"
    assert up, "no upcoming meeting at the live tick"

    # --- online E3
    _aino_e3_path(client, aino)
    _clock(client, "live", E3)
    done = conn.execute(
        "SELECT COUNT(*) c FROM event_meeting WHERE event_id=?"
        " AND status='done'", (E3,)).fetchone()["c"]
    mine = client.get(f"/api/events/{E3}/my", headers=aino).json()
    up = [m for m in mine["meetings"] if m["status"] == "booked"]
    assert done >= 1, "no finished online talk at the live tick"
    assert up, "no upcoming online meeting at the live tick"
    assert any(m["video_url"] and
               m["video_url"].startswith("https://meet.jit.si/")
               for m in mine["meetings"])


def test_aino_choice_employers_keep_two_slots(client):
    """At matching_closed the employers Aino would choose keep >= 2
    free slots, so the matching simulation can still book her."""
    conn = db_mod.connect()
    ev = conn.execute("SELECT starts_at FROM event WHERE id=?",
                      (E1,)).fetchone()
    for eid in ("emp-market-olari", "emp-cafe-koivu", "emp-kirjasto",
                "emp-puhdistamo", "emp-cleaning"):
        ee = conn.execute(
            "SELECT slots FROM employer_event WHERE event_id=?"
            " AND employer_id=?", (E1, eid)).fetchone()
        if not ee:
            continue
        booked = conn.execute(
            "SELECT COUNT(*) c FROM event_meeting WHERE event_id=?"
            " AND employer_id=? AND status='booked'",
            (E1, eid)).fetchone()["c"]
        assert ee["slots"] - booked >= 2, \
            f"{eid}: {ee['slots']} slots, {booked} booked"
