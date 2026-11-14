"""Auth: register, login, logout, /api/me, profile (spec section 3)."""

from __future__ import annotations

from conftest import login


def test_register_resident(client):
    r = client.post("/api/auth/register", json={
        "role": "resident", "name": "Uusi Ihminen",
        "email": "uusi@example.com", "password": "salasana1"})
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["token"]
    assert body["user"]["role"] == "resident"
    assert "password" not in str(body).lower() or "password_hash" not in str(body)
    assert "password_hash" not in str(body)


def test_register_needs_email_or_phone(client):
    r = client.post("/api/auth/register", json={
        "role": "resident", "name": "X", "password": "salasana1"})
    assert r.status_code == 422


def test_register_short_password(client):
    r = client.post("/api/auth/register", json={
        "role": "resident", "name": "X", "email": "x@example.com",
        "password": "short"})
    assert r.status_code == 422


def test_register_duplicate_email(client):
    r = client.post("/api/auth/register", json={
        "role": "resident", "name": "X", "email": "aino@example.com",
        "password": "salasana1"})
    assert r.status_code == 409


def test_register_advisor_forbidden(client):
    r = client.post("/api/auth/register", json={
        "role": "advisor", "name": "X", "email": "x@example.com",
        "password": "salasana1"})
    assert r.status_code == 422


def test_register_employer_creates_company(client):
    r = client.post("/api/auth/register", json={
        "role": "employer", "name": "Essi Esimies",
        "email": "essi@firma.example", "password": "salasana1",
        "employer_name": "Essi Oy"})
    assert r.status_code == 201, r.text
    me = client.get("/api/me", headers={
        "Authorization": f"Bearer {r.json()['token']}"}).json()
    assert me["role"] == "employer"
    assert me["employer_name"] == "Essi Oy"


def test_login_same_401_for_unknown_and_wrong_password(client):
    r1 = client.post("/api/auth/login", json={
        "login": "nosuch@example.com", "password": "whatever9"})
    r2 = client.post("/api/auth/login", json={
        "login": "aino@example.com", "password": "wrongpass1"})
    assert r1.status_code == r2.status_code == 401
    assert r1.json()["detail"] == r2.json()["detail"]


def test_login_by_phone(client):
    h = login(client, "+358 40 111 2223")
    me = client.get("/api/me", headers=h).json()
    assert me["email"] == "aino@example.com"


def test_logout_invalidates_token(client):
    h = login(client, "pekka@example.com")
    r = client.post("/api/auth/logout", headers=h)
    assert r.status_code == 204
    assert client.get("/api/me", headers=h).status_code == 401


def test_me_requires_auth(client):
    assert client.get("/api/me").status_code == 401


def test_profile_get_put(client, aino):
    p = client.get("/api/me/profile", headers=aino)
    assert p.status_code == 200
    assert p.json()["district"] == "otaniemi"
    r = client.put("/api/me/profile", headers=aino, json={
        "contact_method": "sms", "district": "tapiola",
        "fields": ["cleaning"], "availability": ["sat-morning"],
        "max_hours_per_week": 12, "needs": ["seated_work"],
        "languages": [{"language": "Finnish", "level": "C2"}],
        "about": "Updated."})
    assert r.status_code == 200, r.text
    assert r.json()["district"] == "tapiola"
    assert r.json()["needs"] == ["seated_work"]
    again = client.get("/api/me/profile", headers=aino).json()
    assert again["max_hours_per_week"] == 12


def test_profile_forbidden_for_employer(client, sanna):
    assert client.get("/api/me/profile", headers=sanna).status_code == 403


def test_export(client, aino):
    r = client.get("/api/me/export", headers=aino)
    assert r.status_code == 200
    body = r.json()
    assert body["user"]["email"] == "aino@example.com"
    assert "applications" in body and "password_hash" not in str(body)


def test_delete_account_anonymises(client):
    r = client.post("/api/auth/register", json={
        "role": "resident", "name": "Poistuva",
        "email": "poistuva@example.com", "password": "salasana1"})
    h = {"Authorization": f"Bearer {r.json()['token']}"}
    uid = client.get("/api/me", headers=h).json()["id"]
    client.post("/api/applications", headers=h, json={
        "job_id": "job-clean-office", "contact_method": "email",
        "contact_value": "poistuva@example.com", "answer": "I am thorough."})
    r = client.delete("/api/me", headers=h)
    assert r.status_code == 200
    assert client.get("/api/me", headers=h).status_code == 401
    # advisor sees the application anonymised
    ah = login(client, "advisor@example.com")
    r = client.get("/api/audit", headers=ah)
    assert r.status_code == 200
    # the application row still exists but without identity
    import sqlite3, os
    conn = sqlite3.connect(os.environ["TM_DB_PATH"])
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT name, contact_value, answer FROM application"
                       " WHERE user_id IS NULL AND name='Deleted user'"
                       ).fetchone()
    assert row
    assert row["contact_value"] == "" and row["answer"] == ""
    conn.close()
