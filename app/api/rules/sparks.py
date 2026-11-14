"""Sparks (F06): scarce, evidence-paired requests.

Budget = min(5, max(3, round(total_company_slots * 1.5 / talents_registered))).
Each Spark pairs one confirmed claim with one card requirement. Declines and
missed deadlines refund the Spark; the name is revealed only on accept; accept
books the company's first free slot (F08-lite).
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

HELSINKI = ZoneInfo("Europe/Helsinki")
SPARK_TTL_HOURS = 72
SLOT_START_HOUR = 10
SLOT_MINUTES = 20


class SparkError(Exception):
    def __init__(self, status_code: int, detail: str):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail


def now_helsinki() -> datetime:
    return datetime.now(HELSINKI)


def slot_label(event_date: str, index: int) -> str:
    base = datetime.fromisoformat(event_date).replace(
        hour=SLOT_START_HOUR, minute=0, second=0, microsecond=0)
    base += timedelta(minutes=SLOT_MINUTES * index)
    return base.strftime("%a %d %b · %H:%M")


def spark_budget(conn: sqlite3.Connection) -> int:
    ev = conn.execute("SELECT talents_registered FROM event LIMIT 1").fetchone()
    slots = conn.execute("SELECT COALESCE(SUM(slots),0) AS s FROM company").fetchone()["s"]
    talents = ev["talents_registered"] if ev else 1
    return min(5, max(3, round(slots * 1.5 / talents)))


def expire_overdue(conn: sqlite3.Connection) -> None:
    """Unanswered Sparks past their deadline are refunded to the talent."""
    now = now_helsinki().isoformat()
    conn.execute("UPDATE spark SET status='refunded'"
                 " WHERE status='sent' AND deadline < ?", (now,))


def sparks_used(conn: sqlite3.Connection, talent_id: str) -> int:
    """Sparks currently spent (sent or accepted); declined/refunded don't count."""
    expire_overdue(conn)
    row = conn.execute(
        "SELECT COUNT(*) AS n FROM spark WHERE talent_id=? AND status IN ('sent','accepted')",
        (talent_id,)).fetchone()
    return row["n"]


def spark_to_dict(row: sqlite3.Row) -> dict:
    d = {
        "id": row["id"], "talent_id": row["talent_id"], "card_id": row["card_id"],
        "claim_id": row["claim_id"], "requirement_id": row["requirement_id"],
        "status": row["status"], "deadline": row["deadline"],
    }
    if row["note"]:
        d["note"] = row["note"]
    if row["revealed_name"]:
        d["revealed_name"] = row["revealed_name"]
    if row["slot"]:
        d["slot"] = row["slot"]
    return d


def send_spark(conn: sqlite3.Connection, talent_id: str, card_id: str,
               claim_id: str, requirement_id: str, note: str | None) -> dict:
    expire_overdue(conn)
    if note is not None and len(note) > 140:
        raise SparkError(422, "note must be at most 140 characters")

    if not conn.execute("SELECT 1 FROM talent WHERE id=?", (talent_id,)).fetchone():
        raise SparkError(404, f"unknown talent {talent_id}")
    card_row = conn.execute(
        "SELECT status FROM challenge_card WHERE id=?", (card_id,)
    ).fetchone()
    if not card_row:
        raise SparkError(404, f"unknown card {card_id}")
    if card_row["status"] != "approved":
        raise SparkError(409, "challenge card is not approved")
    claim = conn.execute(
        "SELECT * FROM evidence_claim WHERE id=? AND talent_id=?",
        (claim_id, talent_id)).fetchone()
    if not claim:
        raise SparkError(422, "claim does not belong to this talent")
    if not claim["confirmed"]:
        raise SparkError(422, "only confirmed claims can power a Spark")
    req = conn.execute(
        "SELECT 1 FROM card_requirement WHERE id=? AND card_id=?",
        (requirement_id, card_id)).fetchone()
    if not req:
        raise SparkError(422, "requirement does not belong to this card")

    budget = spark_budget(conn)
    if sparks_used(conn, talent_id) >= budget:
        raise SparkError(409, "spark budget used")

    n = conn.execute("SELECT COUNT(*) AS c FROM spark").fetchone()["c"]
    spark_id = f"sp-{n + 1:03d}"
    while conn.execute("SELECT 1 FROM spark WHERE id=?", (spark_id,)).fetchone():
        n += 1
        spark_id = f"sp-{n + 1:03d}"
    deadline = (now_helsinki() + timedelta(hours=SPARK_TTL_HOURS)).isoformat()
    conn.execute(
        "INSERT INTO spark (id,talent_id,card_id,claim_id,requirement_id,note,"
        "status,deadline) VALUES (?,?,?,?,?,?,'sent',?)",
        (spark_id, talent_id, card_id, claim_id, requirement_id, note, deadline))
    conn.commit()
    return spark_to_dict(conn.execute(
        "SELECT * FROM spark WHERE id=?", (spark_id,)).fetchone())


def next_free_slot(conn: sqlite3.Connection, company_id: str) -> str | None:
    company = conn.execute("SELECT slots FROM company WHERE id=?",
                           (company_id,)).fetchone()
    if not company:
        return None
    taken = conn.execute(
        "SELECT COUNT(*) AS n FROM meeting WHERE company_id=?",
        (company_id,)).fetchone()["n"]
    if taken >= company["slots"]:
        return None
    ev = conn.execute("SELECT date FROM event LIMIT 1").fetchone()
    return slot_label(ev["date"], taken)


def respond(conn: sqlite3.Connection, spark_id: str, decision: str,
            reason_chip: str | None) -> dict:
    expire_overdue(conn)
    row = conn.execute("SELECT * FROM spark WHERE id=?", (spark_id,)).fetchone()
    if not row:
        raise SparkError(404, f"unknown spark {spark_id}")
    if row["status"] != "sent":
        raise SparkError(409, f"spark already {row['status']}")

    if decision == "decline":
        requirements = conn.execute(
            "SELECT id,text FROM card_requirement WHERE card_id=?",
            (row["card_id"],),
        ).fetchall()
        allowed_reasons = {item for req in requirements for item in (req["id"], req["text"])}
        if reason_chip and reason_chip not in allowed_reasons:
            raise SparkError(422, "decline reason must come from a card must-have")
        # declined -> the Spark is refunded to the talent's budget
        conn.execute("UPDATE spark SET status='declined', reason_chip=? WHERE id=?",
                     (reason_chip, spark_id))
        conn.commit()
        return spark_to_dict(conn.execute(
            "SELECT * FROM spark WHERE id=?", (spark_id,)).fetchone())

    card = conn.execute("SELECT company_id FROM challenge_card WHERE id=?",
                        (row["card_id"],)).fetchone()
    ident = conn.execute("SELECT name FROM talent_identity WHERE talent_id=?",
                         (row["talent_id"],)).fetchone()
    slot = next_free_slot(conn, card["company_id"])
    if slot is None:
        raise SparkError(409, "company has no meeting slots available")
    conn.execute("UPDATE spark SET status='accepted', revealed_name=?, slot=?,"
                 " reason_chip=? WHERE id=?",
                 (ident["name"] if ident else None, slot, reason_chip, spark_id))
    n = conn.execute("SELECT COUNT(*) AS c FROM meeting").fetchone()["c"]
    meeting_id = f"mt-{n + 1:03d}"
    while conn.execute("SELECT 1 FROM meeting WHERE id=?",
                       (meeting_id,)).fetchone():
        n += 1
        meeting_id = f"mt-{n + 1:03d}"
    conn.execute(
        "INSERT INTO meeting (id,spark_id,company_id,card_id,talent_id,slot)"
        " VALUES (?,?,?,?,?,?)",
        (meeting_id, spark_id, card["company_id"], row["card_id"],
         row["talent_id"], slot))
    conn.commit()
    return spark_to_dict(conn.execute(
        "SELECT * FROM spark WHERE id=?", (spark_id,)).fetchone())
