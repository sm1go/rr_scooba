"""The three seeded demo scenarios (spec section 4 + 6), end to end."""

from __future__ import annotations

from conftest import login


def test_aino_finds_cafe_and_cleaning_jobs(client, aino):
    # her slots: weekday evenings + all of sat/sun
    slots = ("mon-evening,tue-evening,wed-evening,thu-evening,fri-evening,"
             "sat-morning,sat-afternoon,sat-evening,"
             "sun-morning,sun-afternoon,sun-evening")
    jobs = client.get(f"/api/jobs?slots={slots}").json()["jobs"]
    ids = {j["id"] for j in jobs}
    assert "job-cafe-weekend" in ids      # Sat–Sun 10–16
    assert "job-clean-office" in ids      # Tue+Thu 18–21
    # a weekday-morning job is not offered to her
    assert "job-library-shelf" not in ids
    # the café job carries the labels the filters use
    cafe = next(j for j in jobs if j["id"] == "job-cafe-weekend")
    assert "students" in {l["id"] for l in cafe["labels"]}


def test_pekka_finds_library_job(client, pekka):
    jobs = client.get(
        "/api/jobs?slots=mon-morning,wed-morning&hours_max=10").json()["jobs"]
    ids = {j["id"] for j in jobs}
    assert "job-library-shelf" in ids
    lib = next(j for j in jobs if j["id"] == "job-library-shelf")
    assert "retirement" in {l["id"] for l in lib["labels"]}


def test_amira_finds_cs_job_with_needs(client, amira):
    # her needs: step_free + seated. With needs_mode=not_no the customer
    # service job stays in the list (step_free is "not known yet").
    jobs = client.get(
        "/api/jobs?needs=step_free_entrance,seated_work"
        "&needs_mode=not_no").json()["jobs"]
    ids = {j["id"] for j in jobs}
    assert "job-cs-desk" in ids
    cond = {c["key"]: c for c in client.get(
        "/api/jobs/job-cs-desk").json()["conditions"]}
    assert cond["seated_work"]["value"] == "yes"
    assert cond["seated_work"]["source"] == "employer"
    assert cond["step_free_entrance"]["value"] == "unknown"
    # strict mode drops it (step_free is not confirmed yes)
    strict = client.get(
        "/api/jobs?needs=step_free_entrance,seated_work").json()["jobs"]
    assert "job-cs-desk" not in {j["id"] for j in strict}
    # her seeded help request targets that job
    mine = client.get("/api/me/help-requests", headers=amira).json()
    assert any(h["job_id"] == "job-cs-desk"
               and h["kind"] == "check_conditions"
               for h in mine["help_requests"])


def test_sanna_sees_three_applications(client, sanna):
    apps = client.get(
        "/api/employer/applications?job_id=job-cafe-weekend",
        headers=sanna).json()["applications"]
    statuses = {a["status"] for a in apps}
    assert len(apps) >= 3
    assert {"sent", "interview", "not_selected"} <= statuses


def test_advisor_checks_amiras_condition_end_to_end(client, advisor, amira):
    # the smoke walk from the spec: advisor checks the condition → output changes
    hrs = client.get("/api/advisor/help-requests?status=new",
                     headers=advisor).json()["help_requests"]
    target = next(h for h in hrs if h["job_id"] == "job-cs-desk")
    client.post(f"/api/advisor/help-requests/{target['id']}",
                headers=advisor,
                json={"status": "in_progress",
                      "advisor_reply": "Checking the entrance today."})
    for key in target["condition_keys"]:
        client.put(f"/api/advisor/jobs/{target['job_id']}/conditions",
                   headers=advisor,
                   json={"key": key, "value": "yes",
                         "note": "Checked on site."})
    job = client.get("/api/jobs/job-cs-desk").json()
    cond = {c["key"]: c for c in job["conditions"]}
    assert cond["step_free_entrance"]["value"] == "yes"
    assert cond["step_free_entrance"]["source"] == "advisor"
    # Amira now finds the job even in strict mode
    strict = client.get(
        "/api/jobs?needs=step_free_entrance,seated_work",
        headers=amira).json()["jobs"]
    assert "job-cs-desk" in {j["id"] for j in strict}
