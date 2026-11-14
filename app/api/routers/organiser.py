"""Organiser tile (F15/F16-lite), trust lab (F18) and the audit trail."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends

from .. import db as db_mod
from ..rules.pool import band_for

router = APIRouter()

TWIN_REPORT = Path(__file__).resolve().parents[3] / "db" / "seed" / "twin_report.json"


def get_conn():
    conn = db_mod.connect()
    try:
        yield conn
    finally:
        conn.close()


@router.get("/organiser/overview")
def organiser_overview(conn=Depends(get_conn)):
    cards = conn.execute(
        "SELECT COUNT(*) AS n FROM challenge_card WHERE status='approved'").fetchone()["n"]
    sparks = conn.execute("SELECT COUNT(*) AS n FROM spark").fetchone()["n"]
    answered = conn.execute(
        "SELECT COUNT(*) AS n FROM spark WHERE status IN ('accepted','declined')"
    ).fetchone()["n"]
    meetings = conn.execute("SELECT COUNT(*) AS n FROM meeting").fetchone()["n"]

    within = 0
    for m in conn.execute("SELECT id, created_at FROM meeting"):
        cl = conn.execute(
            "SELECT created_at FROM closure WHERE meeting_id=? ORDER BY created_at LIMIT 1",
            (m["id"],)).fetchone()
        if cl:
            try:
                delta = datetime.fromisoformat(cl["created_at"]) - \
                        datetime.fromisoformat(m["created_at"])
                if delta <= timedelta(hours=72):
                    within += 1
            except ValueError:
                pass
    closures_pct = round(100 * within / meetings) if meetings else 0

    no_meeting = conn.execute(
        "SELECT COUNT(*) AS n FROM talent WHERE id NOT IN (SELECT talent_id FROM meeting)"
    ).fetchone()["n"]
    avg_minutes = conn.execute(
        "SELECT COALESCE(AVG(company_minutes_spent),0) AS a FROM challenge_card"
        " WHERE status='approved'").fetchone()["a"]

    return {
        "cards_approved": cards,
        "sparks_sent": sparks,
        "sparks_answered_pct": round(100 * answered / sparks) if sparks else 0,
        "meetings": meetings,
        "closures_within_72h_pct": closures_pct,
        "talents_without_meeting_band": band_for(no_meeting),
        "avg_company_minutes": round(avg_minutes, 1),
    }


@router.get("/trust/twin-report")
def twin_report():
    if TWIN_REPORT.exists():
        report = json.loads(TWIN_REPORT.read_text(encoding="utf-8"))
        report.setdefault("placeholder", False)
        return report
    return {"runs": 0, "pairs": 0, "variants": [], "threshold_pct": 5.0,
            "passed": False, "provider": "mock",
            "generated_at": None,
            "placeholder": True,
            "note": "PRECOMPUTED PLACEHOLDER — real batch runs on Modal (F18)"}


@router.get("/audit")
def audit_log(conn=Depends(get_conn)):
    rows = conn.execute(
        "SELECT at,actor,action,detail FROM audit_log ORDER BY id DESC LIMIT 50"
    ).fetchall()
    return [dict(r) for r in reversed(rows)]
