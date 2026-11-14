"""Shared fixtures: a throwaway SQLite DB built from the real seed."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


@pytest.fixture()
def conn(tmp_path, monkeypatch):
    db_file = tmp_path / "test.sqlite"
    monkeypatch.setenv("TM_DB_PATH", str(db_file))
    from app.api import db
    c = db.connect()
    yield c
    c.close()


@pytest.fixture()
def client(tmp_path, monkeypatch):
    db_file = tmp_path / "api.sqlite"
    monkeypatch.setenv("TM_DB_PATH", str(db_file))
    from fastapi.testclient import TestClient
    from app.api.main import app
    with TestClient(app) as c:
        yield c


def login(client, login: str, password: str = "demo1234") -> dict:
    r = client.post("/api/auth/login",
                    json={"login": login, "password": password})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['token']}"}


@pytest.fixture()
def aino(client):
    return login(client, "aino@example.com")


@pytest.fixture()
def pekka(client):
    return login(client, "pekka@example.com")


@pytest.fixture()
def amira(client):
    return login(client, "amira@example.com")


@pytest.fixture()
def sanna(client):
    return login(client, "sanna@example.com")


@pytest.fixture()
def advisor(client):
    return login(client, "advisor@example.com")


@pytest.fixture()
def register_resident(client):
    def _reg(email="new@example.com", name="Test Person", pw="password9"):
        r = client.post("/api/auth/register", json={
            "role": "resident", "name": name, "email": email, "password": pw})
        assert r.status_code == 201, r.text
        return {"Authorization": f"Bearer {r.json()['token']}"}
    return _reg


@pytest.fixture()
def register_employer(client):
    def _reg(email="boss@example.com", company="Uusi Firma Oy", pw="password9"):
        r = client.post("/api/auth/register", json={
            "role": "employer", "name": "Olli Omistaja", "email": email,
            "password": pw, "employer_name": company})
        assert r.status_code == 201, r.text
        return {"Authorization": f"Bearer {r.json()['token']}"}
    return _reg
