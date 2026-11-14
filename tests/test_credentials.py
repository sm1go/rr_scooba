"""Advisor-checked documents: request -> credential -> share on apply."""

from __future__ import annotations


def _doc_request(client, h, label="Hot work card (tulityökortti)"):
    return client.post("/api/help-requests", headers=h, json={
        "kind": "check_document", "document_label": label,
        "consent": True, "message": "I want this confirmed."})


def test_request_confirm_list_delete(client, aino, pekka, advisor):
    r = _doc_request(client, aino)
    assert r.status_code == 201, r.text
    hr_id = r.json()["id"]

    r = client.post(f"/api/advisor/help-requests/{hr_id}/credential",
                    json={"label": "Hot work card"}, headers=advisor)
    assert r.status_code == 201, r.text

    creds = client.get("/api/me/credentials", headers=aino).json()[
        "credentials"]
    assert any(c["label"] == "Hot work card" for c in creds)
    # not visible to another resident
    others = client.get("/api/me/credentials", headers=pekka).json()[
        "credentials"]
    assert all(c["label"] != "Hot work card" for c in others)

    # another resident cannot delete it
    cid = next(c["id"] for c in creds if c["label"] == "Hot work card")
    assert client.delete(f"/api/me/credentials/{cid}",
                         headers=pekka).status_code == 404
    assert client.delete(f"/api/me/credentials/{cid}",
                         headers=aino).status_code == 204


def test_anonymous_check_document_rejected(client):
    r = client.post("/api/help-requests", json={
        "kind": "check_document", "document_label": "x", "consent": True,
        "name": "No One", "contact_method": "email",
        "contact_value": "n@example.com"})
    assert r.status_code in (401, 422)


def test_share_credentials_snapshot(client, aino, register_employer):
    # aino has a seeded credential (Hygiene passport)
    h = register_employer()
    r = client.post("/api/jobs", headers=h, json={
        "title": "Kitchen help", "field": "restaurant",
        "duties": ["d"], "work_mode": "on_site", "status": "open"})
    job_id = r.json()["id"]
    r = client.post("/api/applications", headers=aino, json={
        "job_id": job_id, "contact_method": "email",
        "contact_value": "a@example.com", "answer": "ok",
        "share_credentials": True})
    assert r.status_code == 201, r.text
    snap = r.json()["shared_credentials"]
    assert snap and snap[0]["label"].startswith("Hygiene")
