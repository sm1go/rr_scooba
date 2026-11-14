"""Working-hours consistency: breaks, rota jobs, employer validation."""

from __future__ import annotations


def _mins(t: str) -> int:
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _effective_hours(job: dict) -> float:
    """Longest shift per day, minus the unpaid break, in hours/week."""
    per: dict[str, int] = {}
    for s in job["shifts"]:
        dur = (_mins(s["end"]) - _mins(s["start"])) % (24 * 60)
        if dur > per.get(s["day"], 0):
            per[s["day"]] = dur
    return sum(per.values()) / 60.0 - len(per) * job["break_min"] / 60.0


def test_seed_hours_consistent(client):
    """Every non-rota, non-flexible seeded job: shifts minus break fit
    inside the stated hours range."""
    r = client.get("/api/jobs")
    assert r.status_code == 200
    bad = []
    for j in r.json()["jobs"]:
        if j["status"] != "open" or not j["shifts"] or j["schedule_flexible"]:
            continue
        if j["rota"]:
            continue
        lo = j["hours_min"] if j["hours_min"] is not None else j["hours_max"]
        eff = _effective_hours(j)
        if not (lo - 0.01 <= eff <= j["hours_max"] + 0.01):
            bad.append((j["id"], round(eff, 2), lo, j["hours_max"]))
    assert not bad, f"inconsistent hours: {bad[:10]}"


def test_terasmetso_mig_fixed(client):
    r = client.get("/api/jobs/job-terasmetso-mig")
    assert r.status_code == 200
    j = r.json()
    assert not j["rota"]
    assert j["break_min"] == 30
    assert j["hours_min"] == j["hours_max"] == 37.5
    assert all(s["end"] == "15:00" for s in j["shifts"])


def test_lahilinja_bus_is_rota(client):
    r = client.get("/api/jobs/job-lahilinja-bus")
    assert r.status_code == 200
    j = r.json()
    assert j["rota"] is True
    assert j["break_min"] == 0


def test_rota_jobs_not_in_bundles(client):
    for hours in (18, 25, 30):
        r = client.get(f"/api/bundles?hours={hours}")
        assert r.status_code == 200, r.text
        ids = [j["id"] for b in r.json()["bundles"] for j in b["jobs"]]
        assert "job-lahilinja-bus" not in ids
        assert all(not j["rota"]
                   for b in r.json()["bundles"] for j in b["jobs"])


def test_break_min_validation(client, sanna):
    payload = {
        "title": "Test job", "field": "retail", "district": "matinkyla",
        "address": "Testikatu 1", "contract": "permanent",
        "experience": "none", "status": "draft",
        "shifts": [{"day": "mon", "start": "09:00", "end": "17:00"}],
        "hours_min": 8, "hours_max": 8,
        "break_min": 20,
    }
    r = client.post("/api/jobs", json=payload, headers=sanna)
    assert r.status_code == 422
    for ok in (0, 15, 30, 45, 60):
        r = client.post("/api/jobs", json={**payload, "break_min": ok},
                        headers=sanna)
        assert r.status_code == 201, (ok, r.text)
        assert r.json()["break_min"] == ok
    r = client.post("/api/jobs",
                    json={**payload, "break_min": 30, "rota": True},
                    headers=sanna)
    assert r.status_code == 201
    assert r.json()["rota"] is True
