"""Shared fixtures: a throwaway SQLite DB built from the real seed."""

from __future__ import annotations

import os
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
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    from fastapi.testclient import TestClient
    from app.api.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def lumo_card(conn):
    from app.api import db
    return db.get_card(conn, "card-co-lumo")


@pytest.fixture()
def draft_card():
    """The recorded Lumo draft card (pre-rewrite, 'fluent' era)."""
    import json
    rec = json.loads((ROOT / "db" / "seed" / "recorded" / "ad_lumo.json")
                     .read_text(encoding="utf-8"))
    return rec["card"]


@pytest.fixture()
def amira_story():
    import json
    return json.loads((ROOT / "db" / "seed" / "recorded" / "amira_story.json")
                      .read_text(encoding="utf-8"))
