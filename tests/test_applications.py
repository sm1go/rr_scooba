"""Applications: create, limit, duplicates, withdraw, status, privacy."""

from __future__ import annotations

from conftest import login


def _apply(client, headers, job_id, **kw):
    body = {"job_id": job_id, "contact_method": "sms",
            "contact_value": "+358 40 000", "answer": "I can do this well."}
    body.update(kw)
    return client.post("/api/applications", headers=headers, json=body)


def test_apply_and_read_back(client, register_resident):
    h = register_resident()
    r = _apply(client, h, "job-clean-office")
    assert r.status_code == 201, r.text
    app = r.json()
    assert app["status"] == "sent"
    mine = client.get("/api/me/applications", headers=h).json()
    assert len(mine["applications"]) == 1
    assert mine["applications"][0]["job"]["id"] == "job-clean-office"


def test_apply_needs_answer(client, register_resident):
    r = _apply(client, register_resident(), "job-clean-office", answer="  ")
    assert r.status_code == 422


def test_apply_cv_required(client, register_resident):
    h = register_resident()
    r = _apply(client, h, "job-lumo-junior")
    assert r.status_code == 422
    r = _apply(client, h, "job-lumo-junior", cv_text="My projects: ...")
    assert r.status_code == 201


def test_duplicate_application_409(client, register_resident):
    h = register_resident()
    assert _apply(client, h, "job-market-shelf").status_code == 201
    assert _apply(client, h, "job-market-shelf").status_code == 409


def test_five_active_limit(client, register_resident):
    h = register_resident()
    job_ids = [j["id"] for j in client.get("/api/jobs").json()["jobs"]
               if not j["cv_required"]][:6]
    for jid in job_ids[:5]:
        assert _apply(client, h, jid).status_code == 201, jid
    r = _apply(client, h, job_ids[5])
    assert r.status_code == 409
    assert "5 open applications" in r.json()["detail"]


def test_apply_to_missing_job(client, register_resident):
    assert _apply(client, register_resident(), "job-nope").status_code == 409


def test_withdraw(client, register_resident):
    h = register_resident()
    app = _apply(client, h, "job-clean-gym").json()
    r = client.post(f"/api/applications/{app['id']}/withdraw", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "withdrawn"
    # a withdrawn application frees the slot and can not be withdrawn again
    assert client.post(f"/api/applications/{app['id']}/withdraw",
                       headers=h).status_code == 409


def test_withdraw_someone_elses(client, aino, register_resident):
    app = _apply(client, register_resident(), "job-clean-gym").json()
    r = client.post(f"/api/applications/{app['id']}/withdraw", headers=aino)
    assert r.status_code == 404


def test_employer_sees_shared_needs_only(client, register_resident, sanna):
    h = register_resident()
    _apply(client, h, "job-cafe-weekend",
           shared_needs=["seated_work", "quiet_environment"])
    apps = client.get("/api/employer/applications", headers=sanna).json()
    me = next(a for a in apps["applications"] if a["name"] == "Test Person")
    assert me["shared_needs"] == ["seated_work", "quiet_environment"]
    # nothing else about the profile leaks
    assert "needs" not in me


def test_status_change_needs_note(client, sanna):
    apps = client.get("/api/employer/applications", headers=sanna).json()
    sent = next(a for a in apps["applications"] if a["status"] == "sent")
    r = client.post(f"/api/applications/{sent['id']}/status", headers=sanna,
                    json={"status": "interview", "status_note": ""})
    assert r.status_code == 422
    r = client.post(f"/api/applications/{sent['id']}/status", headers=sanna,
                    json={"status": "interview",
                          "status_note": "Thursday 15:00 at the café"})
    assert r.status_code == 200
    assert r.json()["status"] == "interview"


def test_status_change_ownership(client, sanna, aino):
    # aino is a resident — cannot set statuses at all
    apps = client.get("/api/employer/applications", headers=sanna).json()
    target = apps["applications"][0]
    r = client.post(f"/api/applications/{target['id']}/status", headers=aino,
                    json={"status": "offer", "status_note": "x"})
    assert r.status_code == 403


def test_employer_only_own_jobs_applications(client, sanna):
    r = client.get("/api/employer/applications?job_id=job-clean-office",
                   headers=sanna)
    assert r.status_code == 403


def test_history_shown_to_resident(client, register_resident, sanna):
    h = register_resident()
    app = _apply(client, h, "job-cafe-weekend").json()
    client.post(f"/api/applications/{app['id']}/status", headers=sanna,
                json={"status": "interview",
                      "status_note": "Friday 14:00"})
    mine = client.get("/api/me/applications", headers=h).json()["applications"]
    me = next(a for a in mine if a["id"] == app["id"])
    assert me["status"] == "interview"
    assert me["status_note"] == "Friday 14:00"
    assert me["history"]


def test_saved_jobs(client, aino):
    assert client.put("/api/me/saved/job-tiima-helper",
                      headers=aino).status_code == 204
    saved = client.get("/api/me/saved", headers=aino).json()["jobs"]
    ids = {j["id"] for j in saved}
    assert {"job-weegee", "job-tiima-helper"} <= ids
    assert client.delete("/api/me/saved/job-tiima-helper",
                         headers=aino).status_code == 204
    saved = client.get("/api/me/saved", headers=aino).json()["jobs"]
    assert "job-tiima-helper" not in {j["id"] for j in saved}


def test_apply_needs_login(client):
    r = client.post("/api/applications", json={
        "job_id": "job-clean-office", "contact_method": "sms",
        "contact_value": "1", "answer": "x"})
    assert r.status_code == 401
