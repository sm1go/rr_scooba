"""Public catalogue: GET /api/catalog + GET /api/event."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from fastapi import APIRouter, Depends

from ..db import get_conn, SEED_DIR
from ..rules.labels import LABELS_META

router = APIRouter(prefix="/api", tags=["catalog"])


def _catalog() -> dict:
    return json.loads((SEED_DIR / "catalog.json").read_text(encoding="utf-8"))


@router.get("/catalog")
def catalog(conn: sqlite3.Connection = Depends(get_conn)):
    """Fields, condition keys with plain labels, label ids, districts with
    coordinates, contract types, language levels. Public, no account."""
    cat = _catalog()
    cat["labels"] = LABELS_META
    cat["availability_parts"] = [
        {"id": "morning", "hours": "06:00–12:00"},
        {"id": "afternoon", "hours": "12:00–17:00"},
        {"id": "evening", "hours": "17:00–23:00"},
    ]
    cat["employers"] = [dict(r) for r in conn.execute(
        "SELECT id, name FROM employer ORDER BY name").fetchall()]
    return cat


@router.get("/event")
def event(conn: sqlite3.Connection = Depends(get_conn)):
    """The next event with participating employers, booths and their open
    jobs (spec v3 §8)."""
    ev = conn.execute("SELECT * FROM event WHERE ends_at >= datetime('now') ORDER BY date LIMIT 1").fetchone()
    if not ev:
        return {"event": None, "employers": []}
    employers = [dict(r) for r in conn.execute(
        "SELECT e.id, e.name, e.tagline, e.field, e.logo_color, ee.booth"
        " FROM employer_event ee"
        " JOIN employer e ON e.id = ee.employer_id"
        " WHERE ee.event_id=? ORDER BY ee.booth", (ev["id"],))]
    for emp in employers:
        emp["jobs"] = [dict(j) for j in conn.execute(
            "SELECT id,title FROM job WHERE employer_id=? AND status='open'"
            " ORDER BY title", (emp["id"],))]
    return {"event": dict(ev), "employers": employers}


@router.get("/support")
def support():
    """City support programmes — verbatim seed data (spec v3 §7).
    Public; eligibility matching happens in the browser."""
    from ..support import catalogue
    return catalogue()
