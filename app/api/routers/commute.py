"""GET /api/commute — HSL public-transport commute estimate (spec v3 §5).

Origin = district centre from the catalogue; destination = job coordinates.
Arrive by the start of the job's first shift on the next such weekday
(jobs without shifts: next weekday 09:00). Results cached 7 days.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from .. import db as db_mod
from .. import digitransit, settings
from ..db import get_conn
from .jobs import _district_center, _decode

router = APIRouter(prefix="/api", tags=["commute"])

CACHE_DAYS = 7
DAY_INDEX = {"mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5,
             "sun": 6}


def arrive_by(job: dict, now: datetime | None = None) -> datetime:
    """Next shift start, or next weekday 09:00 when no shifts."""
    now = now or datetime.now()
    shifts = job.get("shifts") or []
    if shifts:
        best = None
        for s in shifts:
            wd = DAY_INDEX.get(s.get("day"))
            if wd is None:
                continue
            try:
                h, m = (int(x) for x in s["start"].split(":"))
            except (KeyError, ValueError):
                continue
            delta = (wd - now.weekday()) % 7
            if delta == 0 and now >= now.replace(hour=h, minute=m,
                                                 second=0, microsecond=0):
                delta = 7
            cand = (now + timedelta(days=delta)).replace(
                hour=h, minute=m, second=0, microsecond=0)
            if best is None or cand < best:
                best = cand
        if best:
            return best
    delta = 1
    while (now + timedelta(days=delta)).weekday() >= 5:
        delta += 1
    return (now + timedelta(days=delta)).replace(hour=9, minute=0, second=0,
                                                 microsecond=0)


def cached_commute(conn, job_id: str, district: str) -> dict | None:
    """Read the cache only — never calls the routing service."""
    cached = conn.execute(
        "SELECT payload, computed_at FROM commute_cache"
        " WHERE job_id=? AND district=?", (job_id, district)).fetchone()
    if not cached:
        return None
    try:
        at = datetime.fromisoformat(cached["computed_at"])
    except ValueError:
        return None
    if datetime.now() - at >= timedelta(days=CACHE_DAYS):
        return None
    return json.loads(cached["payload"])


def compute_commute(conn, job: dict, district: str) -> dict | None:
    """Cache lookup, else one Digitransit call; returns payload or None.
    Raises CommuteUnavailable when no key / service down."""
    center = _district_center(district)
    if not center or job.get("lat") is None:
        return None
    when = arrive_by(job)
    cached = conn.execute(
        "SELECT payload, computed_at FROM commute_cache"
        " WHERE job_id=? AND district=?", (job["id"], district)).fetchone()
    if cached:
        try:
            at = datetime.fromisoformat(cached["computed_at"])
            if datetime.now() - at < timedelta(days=CACHE_DAYS):
                return json.loads(cached["payload"])
        except ValueError:
            pass
    node = digitransit.get_client().plan(
        center[0], center[1], job["lat"], job["lon"], when)
    payload = digitransit.commute_out(node, when)
    conn.execute(
        "INSERT OR REPLACE INTO commute_cache (job_id,district,payload,"
        "computed_at) VALUES (?,?,?,?)",
        (job["id"], district, json.dumps(payload, ensure_ascii=False),
         datetime.now().isoformat(timespec="seconds")))
    db_mod.audit(conn, "system", "commute_computed",
                 f"{job['id']}:{district}")
    conn.commit()
    return payload


@router.get("/commute")
def commute(job_id: str = Query(), district: str = Query(),
            conn: sqlite3.Connection = Depends(get_conn)):
    """'About 24 min by bus and metro from Matinkylä' — needs a key."""
    if not settings.commute_enabled():
        raise HTTPException(503, "The commute service is not connected.")
    row = conn.execute("SELECT * FROM job WHERE id=? AND status='open'",
                       (job_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Job not found.")
    if not _district_center(district):
        raise HTTPException(422, "Unknown district.")
    try:
        out = compute_commute(conn, _decode(row), district)
    except digitransit.CommuteUnavailable as e:
        raise HTTPException(503, "The commute service is not connected."
                            ) from e
    if out is None:
        raise HTTPException(404, "No route found for that trip.")
    return out
