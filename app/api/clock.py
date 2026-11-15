"""One clock for the whole event journey (spec §9.2).

All phase logic, deadlines and "now" computations go through app_now().
In demo mode the demo clock (demo_state.now) wins; otherwise real UTC.
Event datetimes are stored as naive local ISO strings; the demo clock is
stored the same way so comparisons stay consistent.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

from . import settings


def app_now(conn: sqlite3.Connection | None = None) -> datetime:
    """Naive "now". Demo mode: the demo clock; else real UTC (naive)."""
    if conn is not None and settings.demo_mode():
        row = conn.execute(
            "SELECT value FROM demo_state WHERE key='now'").fetchone()
        if row and row["value"]:
            return datetime.fromisoformat(row["value"])
    return datetime.now(timezone.utc).replace(tzinfo=None)


def set_demo_now(conn: sqlite3.Connection, when: datetime) -> None:
    conn.execute("INSERT OR REPLACE INTO demo_state (key,value)"
                 " VALUES ('now',?)",
                 (when.isoformat(timespec="seconds"),))


def event_phase(ev: sqlite3.Row, conn: sqlite3.Connection | None = None,
                now: datetime | None = None) -> str:
    """registration | matched | live | after | closed (§9.2)."""
    now = now or app_now(conn)

    def _t(v: str) -> datetime:
        return datetime.fromisoformat(v) if v else datetime.max

    mc = _t(ev["matching_closes"])
    sa = _t(ev["starts_at"])
    ea = _t(ev["ends_at"])
    ad = _t(ev["answers_due"])
    if now < mc:
        return "registration"
    if now < sa:
        return "matched"
    if now < ea:
        return "live"
    if now < ad:
        return "after"
    return "closed"
