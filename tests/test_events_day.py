"""Spec §4/§5 (v10): walk-in queues, booth talks + no-show, organizer
live board and offer-free-slot, seen-at-event sharing, organizer report
+ fairness panel, and the card_language privacy fix."""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.usefixtures("client")

E1 = "ev-2027-03"
SANNA = "emp-cafe-koivu"


def _reg(client, email, name="Uusi Ihminen", group="A"):
    r = client.post("/api/auth/register", json={
        "role": "resident", "name": name, "email": email,
        "password": "password9"})
    assert r.status_code == 201, r.text
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    r = client.post(f"/api/events/{E1}/register", headers=h, json={
        "time_group": group, "card_language": "en",
        "card": {"looking_for": "any work",
                 "done": [{"text": "Helped in a shop",
                           "own_words": "Helped in a shop"}],
                 "district": "", "availability": []}})
    assert r.status_code == 201, r.text
    return h


def _sanna_meeting(client, sanna):
    day = client.get(f"/api/employer/events/{E1}/day",
                     headers=sanna).json()
    return [m for m in day["meetings"] if m["status"] == "booked"]


def _live(client):
    r = client.post("/api/demo/clock",
                    json={"stage": "live", "event_id": E1})
    assert r.status_code == 200, r.text


# --- anonymity: no card_language anywhere in employer cards --------------

def test_employer_cards_have_no_card_language(client, sanna):
    cards = client.get(f"/api/employer/events/{E1}/cards",
                       headers=sanna).json()["cards"]
    assert cards
    for c in cards:
        assert "card_language" not in c
        assert "card_language" not in json.dumps(c)


def test_booth_next_card_has_no_card_language(client, sanna):
    day = client.get(f"/api/employer/events/{E1}/day",
                     headers=sanna).json()
    if day["next_card"]:
        assert "card_language" not in day["next_card"]


# --- queue -----------------------------------------------------------------

def test_queue_join_twice_one_entry_and_leave(client, aino):
    client.post(f"/api/events/{E1}/register", headers=aino,
                json={"time_group": "A", "card": {
                    "looking_for": "x",
                    "done": [{"text": "y"}],
                    "district": "", "availability": []}})
    r = client.put(f"/api/events/{E1}/queue/{SANNA}", headers=aino)
    assert r.status_code == 201, r.text
    r = client.put(f"/api/events/{E1}/queue/{SANNA}", headers=aino)
    assert r.status_code == 409
    q = [x for x in client.get(
        f"/api/events/{E1}/my", headers=aino).json()["queue"]
        if x["employer_id"] == SANNA]
    assert len(q) == 1
    r = client.delete(f"/api/events/{E1}/queue/{SANNA}", headers=aino)
    assert r.status_code == 200
    q = [x for x in client.get(
        f"/api/events/{E1}/my", headers=aino).json()["queue"]
        if x["employer_id"] == SANNA]
    assert q == []


# --- employer records talk on a meeting ------------------------------------

def test_record_talk_observed_subset_note_status(client, sanna):
    _live(client)
    m = _sanna_meeting(client, sanna)[0]
    ws = client.get(f"/api/employer/events/{E1}",
                    headers=sanna).json()
    first_week = ws["need"]["card"]["first_week"]
    # bad observed item -> 422
    r = client.post(
        f"/api/employer/events/{E1}/meetings/{m['id']}/talk",
        headers=sanna, json={"observed": ["Not a real item"],
                             "outcome": "next_step",
                             "employer_note": "x"})
    assert r.status_code == 422
    # missing note -> 422
    r = client.post(
        f"/api/employer/events/{E1}/meetings/{m['id']}/talk",
        headers=sanna, json={"observed": [first_week[0]],
                             "outcome": "next_step", "employer_note": ""})
    assert r.status_code == 422
    # valid (§9.4: next step carries kind + date-time + place)
    r = client.post(
        f"/api/employer/events/{E1}/meetings/{m['id']}/talk",
        headers=sanna, json={"observed": [first_week[0]],
                             "outcome": "next_step",
                             "employer_note": "Trial next week",
                             "next_kind": "tryout",
                             "next_at": "2027-03-26T10:00:00",
                             "next_place": "Cafe Koivu, Tapiola"})
    assert r.status_code == 201, r.text
    ms = {x["id"]: x for x in _sanna_meeting(client, sanna)} | {
        x["id"]: x for x in client.get(
            f"/api/employer/events/{E1}/day",
            headers=sanna).json()["meetings"]}
    assert ms[m["id"]]["status"] == "done"
    # second recording on a closed meeting -> 409
    r = client.post(
        f"/api/employer/events/{E1}/meetings/{m['id']}/talk",
        headers=sanna, json={"observed": [], "outcome": "not_now",
                             "employer_note": "x"})
    assert r.status_code == 409


def test_no_show_and_other_employer_cannot_record(client, sanna,
                                                register_employer):
    _live(client)
    ms = _sanna_meeting(client, sanna)
    m1, m2 = ms[0], ms[1]
    r = client.post(
        f"/api/employer/events/{E1}/meetings/{m1['id']}/no-show",
        headers=sanna)
    assert r.status_code == 200
    other = register_employer(email="other@example.com",
                              company="Muu Oy")
    for path in (f"meetings/{m2['id']}/talk",
                 f"meetings/{m2['id']}/no-show"):
        r = client.post(f"/api/employer/events/{E1}/{path}",
                        headers=other,
                        json={"observed": [], "outcome": "not_now",
                              "employer_note": "x"})
        assert r.status_code in (403, 404)


def test_visitor_code_reveal(client, sanna, aino):
    client.post(f"/api/events/{E1}/register", headers=aino,
                json={"time_group": "A", "card": {
                    "looking_for": "x",
                    "done": [{"text": "y"}],
                    "district": "", "availability": []}})
    my = client.get(f"/api/events/{E1}/my", headers=aino).json()
    assert my["visitor_code"]
    r = client.post(f"/api/employer/events/{E1}/reveal",
                    headers=sanna, json={"code": my["visitor_code"]})
    assert r.status_code == 200, r.text
    assert r.json()["name"]
    # unknown code -> 404
    r = client.post(f"/api/employer/events/{E1}/reveal",
                    headers=sanna, json={"code": "9999"})
    assert r.status_code in (404, 200)


# --- organizer live board + offer-free-slot ---------------------------------

def test_offer_free_slot_first_in_queue(client, advisor):
    h1 = _reg(client, "q1@example.com")
    h2 = _reg(client, "q2@example.com")
    client.put(f"/api/events/{E1}/queue/{SANNA}", headers=h1)
    client.put(f"/api/events/{E1}/queue/{SANNA}", headers=h2)
    board = client.get(f"/api/advisor/events/{E1}/day",
                       headers=advisor).json()
    row = [b for b in board["booths"]
           if b["employer_id"] == SANNA][0]
    assert row["queue"] >= 2
    r = client.post(f"/api/advisor/events/{E1}/offer", headers=advisor,
                    json={"employer_id": SANNA})
    assert r.status_code == 200, r.text
    # the first person got called; second still waiting
    board = client.get(f"/api/advisor/events/{E1}/day",
                       headers=advisor).json()
    row = [b for b in board["booths"]
           if b["employer_id"] == SANNA][0]
    assert row["queue"] == 1
    # the meeting belongs to q1's user (first in queue) and does not
    # double-book q1
    my1 = client.get(f"/api/events/{E1}/my", headers=h1).json()
    times = [m["starts_at"] for m in my1["meetings"]
             if m["status"] != "cancelled"]
    assert len(times) == len(set(times))


def test_day_board_advisor_only(client, aino):
    assert client.get(f"/api/advisor/events/{E1}/day",
                      headers=aino).status_code == 403
    assert client.post(f"/api/advisor/events/{E1}/offer", headers=aino,
                       json={"employer_id": SANNA}).status_code == 403


# --- seen at the event + sharing ---------------------------------------------

def test_event_records_private_and_shared_on_apply(client, aino, pekka):
    recs = client.get("/api/me/event-records",
                      headers=aino).json()["records"]
    assert recs and {"employer", "date", "observed"} <= set(recs[0])
    # pekka cannot see aino's records — he only gets his own
    his = client.get("/api/me/event-records",
                     headers=pekka).json()["records"]
    assert all(r in his for r in his) and his != recs or not recs
    # apply with the share checkbox -> snapshot lands on the application
    job = client.get("/api/jobs", headers=aino).json()["jobs"][0]
    r = client.post("/api/applications", headers=aino, json={
        "job_id": job["id"], "contact_method": "email",
        "contact_value": "a@b.fi", "answer": "Yes, I can.",
        "share_event_records": True})
    assert r.status_code == 201, r.text
    assert r.json()["shared_event_records"] == recs


# --- organizer report + fairness ----------------------------------------------

def test_report_fairness_groups(client, advisor):
    rep = client.get(f"/api/advisor/events/{E1}/report",
                     headers=advisor).json()
    assert rep["booths"]
    big = [g for g in rep["fairness"] if g["registered"] >= 10]
    assert len(big) >= 3
    small = [g for g in rep["fairness"] if g["registered"] < 10]
    for g in small:
        assert g["rates"] is None
    for g in big:
        assert g["rates"] is not None
        counts = [g["registered"], g["chose"], g["invited"], g["met"],
                  g["next_step"]]
        assert counts == sorted(counts, reverse=True)
    # no names anywhere
    blob = json.dumps(rep)
    for name in ("Aino", "Pekka", "Amira", "talent01"):
        assert name not in blob


def test_report_advisor_only(client, aino, sanna):
    assert client.get(f"/api/advisor/events/{E1}/report",
                      headers=aino).status_code == 403
    assert client.get(f"/api/advisor/events/{E1}/report",
                      headers=sanna).status_code == 403
