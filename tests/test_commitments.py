"""Fair-hiring promises: seed assignments, filters, validation, queue rules."""

from __future__ import annotations

import json

from conftest import login

MIN_JOB = {
    "title": "Warehouse helper",
    "field": "logistics",
    "address": "Testikatu 1",
    "district": "lepavaara",
    "hours_min": 10, "hours_max": 30,
    "contract": "permanent",
    "experience": "none",
    "status": "open",
}


def _mk_job(client, sanna, **over):
    payload = {**MIN_JOB, **over}
    r = client.post("/api/jobs", json=payload, headers=sanna)
    assert r.status_code == 201, r.text
    return r.json()["id"]


def _apply(client, h, job_id, **over):
    payload = {"job_id": job_id, "contact_method": "email",
               "contact_value": "m@example.com", "answer": "ok", **over}
    return client.post("/api/applications", json=payload, headers=h)


def _set_status(client, h, app_id, status, note="a note"):
    return client.post(f"/api/applications/{app_id}/status",
                       json={"status": status, "status_note": note},
                       headers=h)


def _seed_jobs():
    return json.load(open("db/seed/jobs.json", encoding="utf-8"))


# --- seed -----------------------------------------------------------------

def test_seed_commitment_counts():
    jobs = _seed_jobs()
    for c in ("open_hiring", "guaranteed_talk", "tryout", "skills_first"):
        assert sum(c in j["commitments"] for j in jobs) >= 10, c


def test_seed_open_hiring_constraints():
    for j in _seed_jobs():
        if "open_hiring" in j["commitments"]:
            assert j["experience"] == "none", j["id"]
            assert not j["cv_required"], j["id"]


# --- filtering ------------------------------------------------------------

def test_commit_filter_single(client):
    r = client.get("/api/jobs?commit=open_hiring")
    assert r.status_code == 200
    jobs = r.json()["jobs"]
    assert jobs and all("open_hiring" in j["commitments"] for j in jobs)


def test_commit_filter_all_required(client):
    r = client.get("/api/jobs?commit=open_hiring,tryout")
    jobs = r.json()["jobs"]
    assert all({"open_hiring", "tryout"} <= set(j["commitments"])
               for j in jobs)


# --- create/update validation ---------------------------------------------

def test_create_unknown_commitment_422(client, sanna):
    r = client.post("/api/jobs",
                    json={**MIN_JOB, "commitments": ["nonsense"]},
                    headers=sanna)
    assert r.status_code == 422


def test_create_open_hiring_with_cv_422(client, sanna):
    r = client.post("/api/jobs",
                    json={**MIN_JOB, "commitments": ["open_hiring"],
                          "cv_required": True},
                    headers=sanna)
    assert r.status_code == 422
    assert r.json()["detail"] == "Open hiring jobs cannot ask for a CV."


# --- open hiring queue -----------------------------------------------------

def test_open_hiring_queue_and_order(client, sanna, register_resident):
    job_id = _mk_job(client, sanna, commitments=["open_hiring"])
    h1 = register_resident("r1@example.com")
    h2 = register_resident("r2@example.com")

    r1 = _apply(client, h1, job_id, answer="")
    r2 = _apply(client, h2, job_id, answer="")
    assert r1.status_code == 201 and r2.status_code == 201
    assert r1.json()["queue_position"] == 1
    assert r2.json()["queue_position"] == 2

    app1, app2 = r1.json()["id"], r2.json()["id"]
    # cannot offer #2 while #1 is still waiting
    r = _set_status(client, sanna, app2, "offer")
    assert r.status_code == 409
    assert "sign-up order" in r.json()["detail"]
    # offering #1 first frees #2
    assert _set_status(client, sanna, app1, "offer").status_code == 200
    assert _set_status(client, sanna, app2, "offer").status_code == 200


# --- guaranteed talk -------------------------------------------------------

def test_guaranteed_talk_blocks_early_rejection(client, sanna,
                                                register_resident):
    job_id = _mk_job(client, sanna, commitments=["guaranteed_talk"])
    r = _apply(client, register_resident(), job_id, meets_must_haves=True)
    assert r.json()["meets_must_haves"] is True
    app_id = r.json()["id"]

    r = _set_status(client, sanna, app_id, "not_selected")
    assert r.status_code == 409
    assert "conversation" in r.json()["detail"]
    assert _set_status(client, sanna, app_id, "interview").status_code == 200
    assert _set_status(client, sanna, app_id,
                       "not_selected").status_code == 200


def test_guaranteed_talk_allows_reject_when_not_met(client, sanna,
                                                  register_resident):
    job_id = _mk_job(client, sanna, commitments=["guaranteed_talk"])
    r = _apply(client, register_resident(), job_id, meets_must_haves=False)
    assert _set_status(client, sanna, r.json()["id"],
                       "not_selected").status_code == 200
