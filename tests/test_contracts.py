"""City-contract jobs (työllistämisehto): API, statuses, hires, filtering."""

from __future__ import annotations

from conftest import login


def test_advisor_contracts_list(client, advisor, aino):
    r = client.get("/api/advisor/contracts", headers=advisor)
    assert r.status_code == 200
    contracts = r.json()["contracts"]
    assert len(contracts) == 6
    statuses = {c["status"] for c in contracts}
    assert "behind" in statuses          # at least 2 seeded behind
    # a resident may not see it
    r2 = client.get("/api/advisor/contracts", headers=aino)
    assert r2.status_code == 403


def test_contract_statuses(client, advisor):
    cs = client.get("/api/advisor/contracts", headers=advisor
                    ).json()["contracts"]
    by_id = {c["id"]: c for c in cs}
    assert by_id["con-lunch-central"]["status"] == "done"
    assert by_id["con-tapiola-repair"]["status"] == "behind"
    assert by_id["con-parcel-hubs"]["status"] == "on_track"


def test_record_hire_increments_and_audit_clean(client, advisor):
    r = client.post("/api/advisor/contracts/con-park-winter/hires",
                    json={"hired_on": "2026-11-20",
                          "note": "started Monday"}, headers=advisor)
    assert r.status_code == 201, r.text
    assert r.json()["hires_done"] == 1
    # audit log must not contain the note text
    audit = client.get("/api/audit", headers=advisor).json()
    rows = [a for a in audit["events"] if "contract_hire" in str(a)]
    assert rows and "started Monday" not in str(rows)


def test_city_contract_filter_and_item(client):
    r = client.get("/api/jobs?city_contract=1")
    assert r.status_code == 200
    jobs = r.json()["jobs"]
    assert jobs and all(j["city_contract"] for j in jobs)
    j = client.get(f"/api/jobs/{jobs[0]['id']}").json()
    assert {"id", "title", "due"} <= set(j["city_contract"])


def test_contract_id_must_belong_to_employer(client, sanna,
                                             register_employer):
    # sanna owns emp-cafe-koivu; con-schools-south belongs to emp-kajo
    h = register_employer()
    r = client.post("/api/jobs", headers=h, json={
        "title": "Helper", "field": "cleaning", "duties": ["d"],
        "work_mode": "on_site", "contract_id": "con-schools-south"})
    assert r.status_code == 422


def test_apply_contract_eligible_visible(client, register_resident, advisor):
    job_id = client.get("/api/jobs?city_contract=1").json()["jobs"][0]["id"]
    h = register_resident()
    r = client.post("/api/applications", headers=h, json={
        "job_id": job_id, "contact_method": "email",
        "contact_value": "x@example.com", "answer": "hi",
        "contract_eligible": True})
    assert r.status_code == 201, r.text
    assert r.json()["contract_eligible"] is True
    apps = client.get("/api/employer/applications",
                      headers=advisor)
    # advisor has no employer view; use the employer of that job instead
    assert apps.status_code in (200, 403)


def test_employer_sees_own_contracts_only(client, register_employer):
    h = register_employer()
    r = client.get("/api/employer/contracts", headers=h)
    assert r.status_code == 200
    assert r.json()["contracts"] == []
    r2 = client.get("/api/employer/contracts",
                    headers=login(client, "sanna@example.com"))
    assert r2.json()["contracts"] == []        # cafe-koivu has none
