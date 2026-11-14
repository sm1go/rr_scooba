"""Staff tools: outcome panel, call outcomes, hidden-vacancy call list,
walk-up event talks and event organiser stats."""

from __future__ import annotations

import pytest

ENDPOINTS = [
    ("get", "/api/advisor/employers-to-call", None),
    ("get", "/api/advisor/event-overview", None),
    ("post", "/api/advisor/calls",
     {"job_id": "job-cafe-weekend", "outcome": "no_answer"}),
    ("post", "/api/advisor/event/talks",
     {"employer_id": "emp-cafe-koivu", "first_name": "Ville",
      "contact_method": "phone", "contact_value": "+358 40 123",
      "consent": True}),
]

WALKUP = {"employer_id": "emp-cafe-koivu", "first_name": "Ville",
          "contact_method": "phone", "contact_value": "+358 40 765 4321",
          "job_id": "job-cafe-weekend", "consent": True}


def _audit(client, advisor):
    return client.get("/api/audit?limit=500", headers=advisor).json()["events"]


@pytest.mark.parametrize("method,path,body", ENDPOINTS)
def test_staff_endpoints_advisor_only(client, aino, sanna, method, path, body):
    for h in (aino, sanna):
        r = getattr(client, method)(path, headers=h,
                                    **({"json": body} if body else {}))
        assert r.status_code == 403
    r = getattr(client, method)(path, **({"json": body} if body else {}))
    assert r.status_code == 401


def test_outcome_panel_counts(client, advisor):
    ov = client.get("/api/advisor/overview", headers=advisor).json()
    o7, all_ = ov["outcomes"]["last_7_days"], ov["outcomes"]["all_time"]
    for o in (o7, all_):
        assert set(o["help_requests"]) == {"new", "in_progress", "done"}
        assert set(o["employer_calls"]) == {"still_open", "filled",
                                            "no_answer", "no_vacancy"}
        assert o["interviews"] >= o["offers"]
        assert o["applications"] >= o["applications_by_advisor"]
    assert all_["applications"] >= o7["applications"]
    assert all_["event_talks"]["recorded"] == 2
    assert all_["event_talks"]["answered"] == 1
    assert all_["event_talks"]["unanswered"] == 1
    assert all_["employer_calls"]["no_answer"] == 0

    client.post("/api/advisor/applications", headers=advisor, json={
        "job_id": "job-clean-office", "name": "Walk-in Person",
        "contact_method": "phone", "contact_value": "+358 40 9",
        "answer": "Cleaned a school.", "consent": True})
    client.post("/api/advisor/calls", headers=advisor,
                json={"employer_id": "emp-kajo", "outcome": "no_answer"})
    client.post("/api/advisor/event/talks", headers=advisor, json=WALKUP)
    ov2 = client.get("/api/advisor/overview", headers=advisor).json()
    n7 = ov2["outcomes"]["last_7_days"]
    assert n7["applications_by_advisor"] == o7["applications_by_advisor"] + 1
    assert n7["applications"] == o7["applications"] + 1
    assert n7["employer_calls"]["no_answer"] == 1
    assert n7["event_talks"]["recorded"] == o7["event_talks"]["recorded"] + 1
    assert n7["event_talks"]["unanswered"] == \
        o7["event_talks"]["unanswered"] + 1


def test_call_still_open_confirms_job(client, advisor):
    r = client.post("/api/advisor/calls", headers=advisor,
                    json={"job_id": "job-cafe-weekend",
                          "outcome": "still_open"})
    assert r.status_code == 201, r.text
    assert r.json()["employer_id"] == "emp-cafe-koivu"
    job = client.get("/api/jobs/job-cafe-weekend").json()
    assert job["confirmed_days_ago"] == 0
    ev = _audit(client, advisor)
    assert any(e["action"] == "call_logged" and e["detail"]
               == "emp-cafe-koivu:job-cafe-weekend:still_open" for e in ev)
    assert any(e["action"] == "job_confirmed" for e in ev)


def test_call_filled_closes_job(client, advisor):
    r = client.post("/api/advisor/calls", headers=advisor,
                    json={"job_id": "job-cafe-weekend", "outcome": "filled"})
    assert r.status_code == 201
    job = client.get("/api/jobs/job-cafe-weekend", headers=advisor).json()
    assert job["status"] == "closed"


def test_call_validation(client, advisor):
    r = client.post("/api/advisor/calls", headers=advisor,
                    json={"employer_id": "emp-kajo", "outcome": "filled"})
    assert r.status_code == 422
    r = client.post("/api/advisor/calls", headers=advisor,
                    json={"job_id": "nope", "outcome": "no_answer"})
    assert r.status_code == 404
    r = client.post("/api/advisor/calls", headers=advisor,
                    json={"employer_id": "nope", "outcome": "no_answer"})
    assert r.status_code == 404
    r = client.post("/api/advisor/calls", headers=advisor,
                    json={"employer_id": "emp-kajo", "outcome": "maybe"})
    assert r.status_code == 422


def test_employers_to_call(client, advisor):
    r = client.get("/api/advisor/employers-to-call", headers=advisor)
    assert r.status_code == 200
    emps = {e["id"]: e for e in r.json()["employers"]}
    # seeded firms with no listing are on the list, with contact details
    pyora = emps["emp-pyorapaja"]
    assert pyora["reason"] == "no_open_job"
    assert pyora["contact_phone"] and pyora["latest_job_id"] is None
    assert pyora["last_call"] is None
    assert "emp-cafe-koivu" not in emps        # fresh open jobs

    client.post("/api/advisor/calls", headers=advisor,
                json={"job_id": "job-cafe-weekend", "outcome": "no_answer"})
    client.post("/api/advisor/calls", headers=advisor,
                json={"employer_id": "emp-pyorapaja",
                      "outcome": "no_vacancy"})
    emps = client.get("/api/advisor/employers-to-call",
                      headers=advisor).json()["employers"]
    assert emps[0]["id"] == "emp-cafe-koivu"   # call-again comes first
    assert emps[0]["reason"] == "call_again"
    assert emps[0]["latest_job_id"] == "job-cafe-weekend"
    assert emps[0]["last_call"]["outcome"] == "no_answer"
    assert "emp-pyorapaja" not in {e["id"] for e in emps}


def test_walkup_talk_flow(client, advisor, sanna):
    r = client.post("/api/advisor/event/talks", headers=advisor, json=WALKUP)
    assert r.status_code == 201, r.text
    tid = r.json()["id"]
    # the employer sees it in their talk list with the shared contact
    talks = client.get("/api/employer/event", headers=sanna).json()["talks"]
    tk = next(t for t in talks if t["id"] == tid)
    assert tk["person_name"] == "Ville"
    assert tk["person_contact_value"] == "+358 40 765 4321"
    assert tk["recorded_by_advisor"] is True
    assert tk["job_id"] == "job-cafe-weekend"
    # and can answer it like any other talk
    r = client.post(f"/api/employer/event/talks/{tid}/answer", headers=sanna,
                    json={"outcome": "next_step", "employer_note": "Call Mon."})
    assert r.status_code == 200
    assert r.json()["person_name"] == "Ville"
    # nothing personal in the audit log
    for e in _audit(client, advisor):
        assert "Ville" not in e["detail"]
        assert "765" not in e["detail"]


def test_walkup_talk_in_unanswered_followup(client, advisor):
    r = client.post("/api/advisor/event/talks", headers=advisor, json=WALKUP)
    tid = r.json()["id"]
    from app.api import db
    c = db.connect()
    c.execute("UPDATE event_talk SET talked_at=datetime('now','-10 days')"
              " WHERE id=?", (tid,))
    c.commit()
    c.close()
    ov = client.get("/api/advisor/overview", headers=advisor).json()
    tk = next(t for t in ov["event_talks_unanswered"] if t["id"] == tid)
    assert tk["person_name"] == "Ville"
    assert tk["recorded_by_advisor"] is True


def test_walkup_talk_validation(client, advisor):
    r = client.post("/api/advisor/event/talks", headers=advisor,
                    json={**WALKUP, "consent": False})
    assert r.status_code == 422
    r = client.post("/api/advisor/event/talks", headers=advisor,
                    json={**WALKUP, "employer_id": "emp-kajo",
                          "job_id": None})
    assert r.status_code == 404                 # no booth
    r = client.post("/api/advisor/event/talks", headers=advisor,
                    json={**WALKUP, "job_id": "job-clean-school"})
    assert r.status_code == 404                 # other employer's job
    r = client.post("/api/advisor/event/talks", headers=advisor,
                    json={**WALKUP, "first_name": ""})
    assert r.status_code == 422


def test_event_overview(client, advisor):
    r = client.get("/api/advisor/event-overview", headers=advisor)
    assert r.status_code == 200
    body = r.json()
    booths = [e["booth"] for e in body["employers"]]
    assert booths == sorted(booths)
    cafe = next(e for e in body["employers"]
                if e["employer_id"] == "emp-cafe-koivu")
    assert cafe["talks"] == 2 and cafe["answered"] == 1
    assert cafe["answered_pct"] == 50 and cafe["next_step"] == 1
    assert body["totals"]["talks"] == 2
    client.post("/api/advisor/event/talks", headers=advisor, json=WALKUP)
    cafe = next(e for e in client.get("/api/advisor/event-overview",
                                      headers=advisor).json()["employers"]
                if e["employer_id"] == "emp-cafe-koivu")
    assert cafe["talks"] == 3 and cafe["answered_pct"] == 33
