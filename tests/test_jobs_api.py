"""GET /api/jobs: filters, shapes, ordering, identical-for-all output."""

from __future__ import annotations


def _jobs(client, **params):
    qs = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
    r = client.get(f"/api/jobs?{qs}")
    assert r.status_code == 200, r.text
    return r.json()["jobs"]


def test_jobs_public_and_count(client):
    jobs = _jobs(client)
    assert len(jobs) == 158


def test_job_item_shape(client):
    j = _jobs(client)[0]
    for key in ("id", "title", "field", "duties", "district", "lat", "lon",
                "work_mode", "pay_amount", "pay_unit", "shifts",
                "schedule_flexible", "hours_min", "hours_max", "contract",
                "experience", "qualifications", "onboarding", "languages",
                "apply_question", "cv_required", "positions", "status",
                "source", "confirmed_at", "employer", "labels", "conditions",
                "event", "confirmed_days_ago", "stale"):
        assert key in j, key
    assert set(j["employer"].keys()) == {"id", "name"}
    assert len(j["conditions"]) == 10
    for c in j["conditions"]:
        assert c["value"] in ("yes", "no", "unknown")
        assert set(c.keys()) == {"key", "value", "source", "checked_at", "note"}
    for label in j["labels"]:
        assert label["why"].strip()


def test_no_score_keys(client):
    def scan(node):
        if isinstance(node, dict):
            for k, v in node.items():
                assert k not in ("score", "rank", "rating"), k
                scan(v)
        elif isinstance(node, list):
            for v in node:
                scan(v)
    for path in ("/api/jobs", "/api/catalog", "/api/event",
                 "/api/jobs/job-cafe-weekend"):
        scan(client.get(path).json())


def test_filter_field(client):
    jobs = _jobs(client, field="cleaning")
    assert jobs and all(j["field"] == "cleaning" for j in jobs)


def test_filter_label(client):
    for label in ("students", "retirement", "first_job", "side_job",
                  "part_time", "access_info"):
        jobs = _jobs(client, label=label)
        assert jobs, label
        assert all(label in {l["id"] for l in j["labels"]} for j in jobs)


def test_filter_slots(client):
    jobs = _jobs(client, slots="tue-evening,thu-evening")
    ids = {j["id"] for j in jobs}
    assert "job-clean-office" in ids
    assert "job-cafe-weekend" not in ids


def test_filter_hours_max(client):
    jobs = _jobs(client, hours_max=10)
    assert jobs and all(j["hours_max"] <= 10 for j in jobs)


def test_filter_pay(client):
    jobs = _jobs(client, pay_min=14, pay_unit="hour")
    assert jobs
    assert all(j["pay_unit"] == "hour" and j["pay_amount"] >= 14
               for j in jobs)


def test_filter_contract_experience_workmode(client):
    assert all(j["contract"] == "summer_job"
               for j in _jobs(client, contract="summer_job"))
    assert all(j["experience"] == "none"
               for j in _jobs(client, experience="none"))
    jobs = _jobs(client, work_mode="remote")
    assert jobs and all(j["work_mode"] == "remote" for j in jobs)


def test_filter_language(client):
    jobs = _jobs(client, language="Finnish", level_max="A2")
    assert jobs
    for j in jobs:
        need = [n for n in j["languages"]
                if n["language"].lower() == "finnish"]
        assert not need or need[0]["level"] in ("A1", "A2")


def test_filter_needs_yes(client):
    jobs = _jobs(client, needs="seated_work")
    assert jobs
    for j in jobs:
        assert {c["key"]: c["value"] for c in j["conditions"]
                }["seated_work"] == "yes"


def test_filter_needs_not_no(client):
    jobs = _jobs(client, needs="step_free_entrance", needs_mode="not_no")
    assert jobs
    for j in jobs:
        assert {c["key"]: c["value"] for c in j["conditions"]
                }["step_free_entrance"] != "no"
    # stricter mode returns fewer or equal results
    strict = _jobs(client, needs="step_free_entrance")
    assert len(strict) <= len(jobs)


def test_filter_district_km_and_distance(client):
    jobs = _jobs(client, district="tapiola", km=3)
    assert jobs
    for j in jobs:
        assert j["work_mode"] == "remote" or j["distance_km"] <= 3
    assert any("distance_km" in j for j in jobs)


def test_filter_at_event(client):
    jobs = _jobs(client, at_event=1)
    assert jobs and all(j["event"] for j in jobs)


def test_filter_q(client):
    jobs = _jobs(client, q="library")
    assert jobs
    assert any("library" in (j["title"] + " ".join(j["duties"])).lower()
               or "library" in j["employer"]["name"].lower() for j in jobs)


def test_order_confirmed_desc(client):
    jobs = _jobs(client)
    dates = [j["confirmed_at"] for j in jobs]
    assert dates == sorted(dates, reverse=True)


def test_stale_flag(client):
    jobs = _jobs(client)
    stale = [j for j in jobs if j["stale"]]
    # expected count is date-dependent: stale == confirmed > 14 days ago
    assert len(stale) == len(
        [j for j in jobs if j["confirmed_days_ago"] > 14])
    assert all(j["confirmed_days_ago"] > 14 for j in stale)
    assert all(j["stale"] or j["confirmed_days_ago"] <= 14 for j in jobs)


def test_get_one_job(client):
    j = client.get("/api/jobs/job-cs-desk").json()
    assert j["id"] == "job-cs-desk"
    cond = {c["key"]: c for c in j["conditions"]}
    assert cond["seated_work"]["value"] == "yes"
    assert cond["step_free_entrance"]["value"] == "unknown"


def test_identical_output_anonymous_and_signed_in(client, aino):
    anon = client.get("/api/jobs").json()
    signed = client.get("/api/jobs", headers=aino).json()
    assert anon == signed


def test_draft_and_closed_hidden(client):
    # all seeded jobs are open; create a draft as an employer and confirm 404
    from conftest import login
    h = login(client, "sanna@example.com")
    r = client.post("/api/jobs", headers=h, json={
        "title": "Secret draft", "status": "draft",
        "work_mode": "on_site", "duties": ["X"]})
    assert r.status_code == 201
    jid = r.json()["id"]
    assert client.get(f"/api/jobs/{jid}").status_code == 404
    assert client.get(f"/api/jobs/{jid}", headers=h).status_code == 200
