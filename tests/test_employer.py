"""Employer: profile, own jobs, job lifecycle, conditions, wording."""

from __future__ import annotations

from conftest import login


def test_employer_profile(client, sanna):
    e = client.get("/api/employer", headers=sanna).json()
    assert e["name"] == "Kahvila Koivu"
    assert e["event"]["booth"] == "A1"
    r = client.put("/api/employer", headers=sanna, json={
        "about": "Two rooms and a terrace.",
        "contact_name": "Sanna", "contact_email": "sanna@koivu.example",
        "contact_phone": "+358 40 1"})
    assert r.status_code == 200
    assert r.json()["about"] == "Two rooms and a terrace."
    assert r.json()["name"] == "Kahvila Koivu"   # unchanged when not sent


def test_employer_jobs_only_own(client, sanna):
    jobs = client.get("/api/employer/jobs", headers=sanna).json()["jobs"]
    ids = {j["id"] for j in jobs}
    assert ids == {"job-cafe-weekend", "job-cafe-weekday"}
    assert all("applications_count" in j for j in jobs)


def test_create_draft_publish_confirm_close(client, register_employer):
    h = register_employer()
    r = client.post("/api/jobs", headers=h, json={
        "title": "Evening helper", "field": "cleaning",
        "duties": ["Clean the office."], "work_mode": "on_site",
        "status": "draft", "experience": "none", "contract": "permanent",
        "conditions": {"seated_work": "yes", "lift": "no"}})
    assert r.status_code == 201, r.text
    job = r.json()
    assert job["status"] == "draft"
    cond = {c["key"]: c["value"] for c in job["conditions"]}
    assert cond["seated_work"] == "yes" and cond["lift"] == "no"

    r = client.post(f"/api/jobs/{job['id']}/publish", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "open"
    # now visible publicly
    assert client.get(f"/api/jobs/{job['id']}").status_code == 200

    assert client.post(f"/api/jobs/{job['id']}/confirm",
                       headers=h).status_code == 200
    confirmed = client.get(f"/api/jobs/{job['id']}").json()
    assert confirmed["confirmed_days_ago"] == 0
    assert confirmed["stale"] is False

    r = client.post(f"/api/jobs/{job['id']}/close", headers=h)
    assert r.status_code == 200
    assert r.json()["status"] == "closed"
    assert client.get(f"/api/jobs/{job['id']}").status_code == 404


def test_close_moves_applications_to_job_closed(client, sanna,
                                                 register_resident):
    h = register_resident()
    app = client.post("/api/applications", headers=h, json={
        "job_id": "job-cafe-weekday", "contact_method": "sms",
        "contact_value": "1", "answer": "I am fast and friendly."}).json()
    client.post("/api/jobs/job-cafe-weekday/close", headers=sanna)
    mine = client.get("/api/me/applications", headers=h).json()
    me = next(a for a in mine["applications"] if a["id"] == app["id"])
    assert me["status"] == "job_closed"


def test_job_ownership_403(client, sanna, register_employer):
    other = register_employer("other@example.com", "Muu Oy")
    r = client.put("/api/jobs/job-cafe-weekend", headers=other, json={
        "title": "Hijacked", "work_mode": "on_site"})
    assert r.status_code == 403
    for act in ("confirm", "close", "publish"):
        assert client.post(f"/api/jobs/job-cafe-weekend/{act}",
                           headers=other).status_code == 403
    # resident cannot create jobs
    from conftest import login as l2
    ah = l2(client, "aino@example.com")
    assert client.post("/api/jobs", headers=ah, json={
        "title": "x", "work_mode": "on_site"}).status_code == 403
    assert sanna


def test_check_wording_tips(client, sanna):
    r = client.post("/api/jobs/check-wording", headers=sanna, json={
        "title": "Young and energetic cleaner wanted",
        "experience_note": "Must be a native Finnish speaker",
        "duties": ["Clean offices", "Take a photo for our wall"],
        "languages": [{"language": "Finnish", "level": "C2", "task": ""}]})
    assert r.status_code == 200
    rules = {t["rule"] for t in r.json()["tips"]}
    assert "age_words" in rules
    assert "native_language" in rules or "language_without_task" in rules
    assert "photo" in rules


def test_publish_blocked_on_protected_requirement(client, register_employer):
    h = register_employer()
    r = client.post("/api/jobs", headers=h, json={
        "title": "Helper", "work_mode": "on_site", "status": "draft",
        "qualifications": ["Must be under 30 and healthy"]})
    jid = r.json()["id"]
    r = client.post(f"/api/jobs/{jid}/publish", headers=h)
    assert r.status_code == 422
    # fixing the wording lets it through
    r = client.put(f"/api/jobs/{jid}", headers=h, json={
        "title": "Helper", "work_mode": "on_site", "status": "draft",
        "qualifications": ["Right to work in Finland"]})
    assert r.status_code == 200
    assert client.post(f"/api/jobs/{jid}/publish",
                       headers=h).status_code == 200


def test_employer_write_keeps_advisor_rows(client, sanna, advisor):
    # advisor checks a condition on Sanna's café job
    client.put("/api/advisor/jobs/job-cafe-weekend/conditions", headers=advisor,
               json={"key": "quiet_environment", "value": "yes",
                     "note": "Checked on a visit."})
    # employer rewrites the job without touching that key's truth
    client.put("/api/jobs/job-cafe-weekend", headers=sanna, json={
        "title": "Café worker — weekends", "work_mode": "on_site",
        "conditions": {"quiet_environment": "yes"}})
    cond = {c["key"]: c for c in client.get(
        "/api/jobs/job-cafe-weekend").json()["conditions"]}
    assert cond["quiet_environment"]["value"] == "yes"
    assert cond["quiet_environment"]["source"] == "advisor"
    # employer stating a *different* value flips the source back
    client.put("/api/jobs/job-cafe-weekend", headers=sanna, json={
        "title": "Café worker — weekends", "work_mode": "on_site",
        "conditions": {"quiet_environment": "no"}})
    cond = {c["key"]: c for c in client.get(
        "/api/jobs/job-cafe-weekend").json()["conditions"]}
    assert cond["quiet_environment"]["value"] == "no"
    assert cond["quiet_environment"]["source"] == "employer"


def test_job_endpoints_need_auth(client):
    assert client.post("/api/jobs", json={"title": "x"}).status_code == 401
    assert client.get("/api/employer").status_code == 401
