"""Advisor: help queue, conditions, employers, apply-for-someone, overview."""

from __future__ import annotations

from conftest import login


def test_help_request_queue(client, advisor):
    r = client.get("/api/advisor/help-requests", headers=advisor)
    assert r.status_code == 200
    hrs = r.json()["help_requests"]
    seeded = next(h for h in hrs if h["id"] == "hr-001")
    assert seeded["kind"] == "check_conditions"
    assert seeded["condition_keys"] == ["step_free_entrance"]
    assert seeded["job"]["id"] == "job-cs-desk"

    r = client.post("/api/advisor/help-requests/hr-001", headers=advisor,
                    json={"status": "in_progress",
                          "advisor_reply": "I will visit on Monday."})
    assert r.status_code == 200
    assert r.json()["status"] == "in_progress"


def test_help_request_visible_to_owner(client, advisor, amira):
    client.post("/api/advisor/help-requests/hr-001", headers=advisor,
                json={"status": "done",
                      "advisor_reply": "The entrance is step-free."})
    mine = client.get("/api/me/help-requests", headers=amira).json()
    req = mine["help_requests"][0]
    assert req["status"] == "done"
    assert req["advisor_reply"] == "The entrance is step-free."


def test_advisor_condition_check_changes_job_output(client, advisor):
    before = client.get("/api/jobs/job-cs-desk").json()
    assert {c["key"]: c["value"] for c in before["conditions"]
            }["step_free_entrance"] == "unknown"
    r = client.put("/api/advisor/jobs/job-cs-desk/conditions", headers=advisor,
                   json={"key": "step_free_entrance", "value": "yes",
                         "note": "Step-free via the Sello lift, checked."})
    assert r.status_code == 200
    cond = {c["key"]: c for c in r.json()["conditions"]}
    assert cond["step_free_entrance"]["value"] == "yes"
    assert cond["step_free_entrance"]["source"] == "advisor"
    assert cond["step_free_entrance"]["note"]


def test_condition_check_role_guard(client, sanna):
    r = client.put("/api/advisor/jobs/job-cs-desk/conditions", headers=sanna,
                   json={"key": "lift", "value": "yes"})
    assert r.status_code == 403


def test_advisor_add_employer_and_job(client, advisor):
    r = client.post("/api/advisor/employers", headers=advisor, json={
        "name": "Pieni Puoti", "contact_name": "Kalle"})
    assert r.status_code == 201
    emp_id = r.json()["id"]
    r = client.post("/api/jobs", headers=advisor, json={
        "title": "Shop help", "field": "retail", "employer_id": emp_id,
        "work_mode": "on_site", "status": "open",
        "duties": ["Help customers."]})
    assert r.status_code == 201
    assert r.json()["source"] == "advisor"


def test_advisor_apply_for_someone(client, advisor):
    r = client.post("/api/advisor/applications", headers=advisor, json={
        "job_id": "job-clean-office", "name": "Walk-in Person",
        "contact_method": "phone", "contact_value": "+358 40 9",
        "answer": "They have cleaned a school for two years.",
        "consent": True})
    assert r.status_code == 201, r.text
    assert r.json()["created_by_advisor"] is True
    # consent is required
    r = client.post("/api/advisor/applications", headers=advisor, json={
        "job_id": "job-clean-office", "name": "No Consent",
        "contact_method": "phone", "contact_value": "1",
        "answer": "x", "consent": False})
    assert r.status_code == 422


def test_advisor_overview(client, advisor):
    r = client.get("/api/advisor/overview", headers=advisor)
    assert r.status_code == 200
    body = r.json()
    assert body["open_jobs"] == 60
    assert len(body["stale_jobs"]) == 8
    assert any(w["days_waiting"] > 7 for w in body["waiting_over_7_days"])
    assert body["new_help_requests"] >= 1
    assert "sent" in body["applications_by_status"]


def test_audit_advisor_only(client, advisor, sanna, aino):
    assert client.get("/api/audit", headers=advisor).status_code == 200
    assert client.get("/api/audit", headers=sanna).status_code == 403
    assert client.get("/api/audit", headers=aino).status_code == 403
    assert client.get("/api/audit").status_code == 401


def test_audit_has_no_secrets(client, advisor, register_resident):
    h = register_resident()
    client.post("/api/applications", headers=h, json={
        "job_id": "job-clean-office", "contact_method": "sms",
        "contact_value": "1", "answer": "Careful and steady.",
        "shared_needs": ["seated_work"]})
    r = client.get("/api/audit", headers=advisor).json()
    blob = str(r).lower()
    for word in ("password", "demo1234", "token", "seated_work",
                 "shared_needs"):
        assert word not in blob, word


def test_advisor_edits_any_job(client, advisor):
    r = client.put("/api/jobs/job-cafe-weekend", headers=advisor, json={
        "title": "Café worker — weekends", "work_mode": "on_site",
        "pay_note": "Sunday bonus paid."})
    assert r.status_code == 200
    assert r.json()["pay_note"] == "Sunday bonus paid."


def test_help_request_without_account(client):
    r = client.post("/api/help-requests", json={
        "kind": "other", "message": "I need help applying.",
        "consent": True, "name": "Anonyymi",
        "contact_method": "phone", "contact_value": "+358 40 8"})
    assert r.status_code == 201, r.text
    # anonymous needs name + contact
    r = client.post("/api/help-requests", json={
        "kind": "other", "message": "x", "consent": True})
    assert r.status_code == 422


def test_help_request_consent_required(client, aino):
    r = client.post("/api/help-requests", headers=aino, json={
        "kind": "prepare_application", "message": "x", "consent": False})
    assert r.status_code == 422


def test_advisor_queue_resident_403(client, aino):
    assert client.get("/api/advisor/help-requests",
                      headers=aino).status_code == 403
    assert client.get("/api/advisor/overview", headers=aino).status_code == 403
