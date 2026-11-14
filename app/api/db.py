"""SQLite access: connect, schema, seed loading.

`db/talentmatch.sqlite` is a build artifact (git-ignored). It is rebuilt from
`db/schema.sql` + `db/seed/*.json` on startup whenever the file is missing, and
the seed itself is regenerated via `scripts/generate_synthetic.py` if absent.
Override the path with the env var `TM_DB_PATH` (used by tests).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "db"
DEFAULT_DB = DB_DIR / "talentmatch.sqlite"
SCHEMA_SQL = DB_DIR / "schema.sql"
SEED_DIR = DB_DIR / "seed"
GENERATOR = ROOT / "scripts" / "generate_synthetic.py"

SEED_REQUIRED = [
    "event.json", "companies.json", "cards.json", "talents.json",
    "identities.json", "sparks.json", "meetings.json", "closures.json",
]


def db_path() -> Path:
    return Path(os.environ.get("TM_DB_PATH", str(DEFAULT_DB)))


def _load_seed(name: str, seed_dir: Path):
    return json.loads((seed_dir / name).read_text(encoding="utf-8"))


def _run_generator() -> None:
    spec = importlib.util.spec_from_file_location("generate_synthetic", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load seed generator at {GENERATOR}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


def ensure_db(path: Path | None = None) -> Path:
    """Create + seed the database file if it does not exist. Returns the path."""
    path = path or db_path()
    if path.exists():
        # Apply the one additive migration needed by databases from earlier runs.
        with closing(sqlite3.connect(path)) as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS evidence_proposal (
                    id TEXT PRIMARY KEY,
                    talent_id TEXT NOT NULL REFERENCES talent(id),
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL DEFAULT (datetime('now'))
                );
                CREATE INDEX IF NOT EXISTS idx_proposal_talent
                    ON evidence_proposal(talent_id);
            """)
        return path
    path.parent.mkdir(parents=True, exist_ok=True)

    missing_seed = any(not (SEED_DIR / f).exists() for f in SEED_REQUIRED)
    if missing_seed:
        _run_generator()

    now = datetime.now().astimezone()
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(SCHEMA_SQL.read_text(encoding="utf-8"))
        _seed(conn, SEED_DIR, now)
        conn.commit()
    finally:
        conn.close()
    return path


def _seed(conn: sqlite3.Connection, seed_dir: Path, now: datetime) -> None:
    ev = _load_seed("event.json", seed_dir)
    conn.execute(
        "INSERT INTO event VALUES (:id,:name,:date,:format,:companies_declared,:talents_registered)",
        ev)

    for c in _load_seed("companies.json", seed_dir):
        conn.execute(
            "INSERT INTO company (id,event_id,name,size,city,contact_name,slots)"
            " VALUES (:id,:event_id,:name,:size,:city,:contact_name,:slots)", c)

    for card in _load_seed("cards.json", seed_dir):
        _insert_card(conn, card)

    for t in _load_seed("talents.json", seed_dir):
        conn.execute(
            "INSERT INTO talent (id,pseudonym,languages,availability,pool_consent)"
            " VALUES (:id,:pseudonym,:languages,:availability,:pool_consent)",
            {**t, "languages": json.dumps(t["languages"], ensure_ascii=False)})
        conn.execute("INSERT INTO evidence_card (talent_id,headline) VALUES (?,?)",
                     (t["id"], t.get("headline", "")))
        for cl in t.get("claims", []):
            conn.execute(
                "INSERT INTO evidence_claim (id,talent_id,text,quote,esco_uri,esco_label,"
                "evidence_level,confirmed,original_language,translated)"
                " VALUES (:id,:talent_id,:text,:quote,:esco_uri,:esco_label,"
                ":evidence_level,:confirmed,:original_language,:translated)",
                {**cl, "talent_id": t["id"]})

    for i in _load_seed("identities.json", seed_dir):
        conn.execute("INSERT INTO talent_identity VALUES (:talent_id,:name,:city)", i)

    for s in _load_seed("sparks.json", seed_dir):
        deadline = now + timedelta(hours=s["deadline_hours"])
        conn.execute(
            "INSERT INTO spark (id,talent_id,card_id,claim_id,requirement_id,note,status,"
            "deadline,reason_chip,revealed_name,slot,created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (s["id"], s["talent_id"], s["card_id"], s["claim_id"], s["requirement_id"],
             s.get("note"), s["status"], deadline.isoformat(), s.get("reason_chip"),
             None, s.get("slot"), now.isoformat()))

    for m in _load_seed("meetings.json", seed_dir):
        conn.execute(
            "INSERT INTO meeting (id,spark_id,company_id,card_id,talent_id,slot,created_at)"
            " VALUES (?,?,?,?,?,?,?)",
            (m["id"], m["spark_id"], m["company_id"], m["card_id"], m["talent_id"],
             m.get("slot"), now.isoformat()))
        # accepted seeded sparks get their revealed name + slot persisted
        ident = conn.execute("SELECT name FROM talent_identity WHERE talent_id=?",
                             (m["talent_id"],)).fetchone()
        conn.execute("UPDATE spark SET revealed_name=?, slot=? WHERE id=?",
                     (ident["name"] if ident else None, m.get("slot"), m["spark_id"]))

    for cl in _load_seed("closures.json", seed_dir):
        created = now - timedelta(hours=cl.get("created_hours_ago", 0))
        conn.execute(
            "INSERT INTO closure (id,meeting_id,outcome,reason_chips,next_step,"
            "redirect_company_id,message_to_talent,support_banner,created_at)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (cl["id"], cl["meeting_id"], cl["outcome"], json.dumps(cl["reason_chips"]),
             cl.get("next_step"), cl.get("redirect_company_id"),
             cl.get("message_to_talent", ""), cl.get("support_banner"),
             created.isoformat()))


def _insert_card(conn: sqlite3.Connection, card: dict) -> None:
    conn.execute(
        "INSERT OR REPLACE INTO challenge_card (id,company_id,title,problem_90d,"
        "nice_to_haves,languages,work_mode,status,company_minutes_spent)"
        " VALUES (:id,:company_id,:title,:problem_90d,:nice_to_haves,:languages,"
        ":work_mode,:status,:company_minutes_spent)",
        {**card,
         "nice_to_haves": json.dumps(card.get("nice_to_haves", []), ensure_ascii=False),
         "languages": json.dumps(card.get("languages", []), ensure_ascii=False)})
    conn.execute("DELETE FROM card_requirement WHERE card_id=?", (card["id"],))
    for pos, r in enumerate(card.get("must_haves", [])):
        existing = conn.execute(
            "SELECT card_id FROM card_requirement WHERE id=?", (r["id"],)
        ).fetchone()
        if existing and existing["card_id"] != card["id"]:
            r["id"] = f"{card['id']}::{r['id']}"
        conn.execute(
            "INSERT OR REPLACE INTO card_requirement (id,card_id,position,text,"
            "how_we_check,esco_uri,esco_label) VALUES (?,?,?,?,?,?,?)",
            (r["id"], card["id"], pos, r["text"], r.get("how_we_check", ""),
             r.get("esco_uri"), r.get("esco_label")))


def save_card(conn: sqlite3.Connection, card: dict) -> None:
    _insert_card(conn, card)


def card_from_row(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    reqs = conn.execute(
        "SELECT id,text,how_we_check,esco_uri,esco_label FROM card_requirement"
        " WHERE card_id=? ORDER BY position", (row["id"],)).fetchall()
    return {
        "id": row["id"], "company_id": row["company_id"], "title": row["title"],
        "problem_90d": row["problem_90d"],
        "must_haves": [dict(r) for r in reqs],
        "nice_to_haves": json.loads(row["nice_to_haves"] or "[]"),
        "languages": json.loads(row["languages"] or "[]"),
        "work_mode": row["work_mode"], "status": row["status"],
        "company_minutes_spent": row["company_minutes_spent"],
    }


def get_card(conn: sqlite3.Connection, card_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM challenge_card WHERE id=?",
                       (card_id,)).fetchone()
    return card_from_row(conn, row) if row else None


def connect(path: Path | None = None) -> sqlite3.Connection:
    """Fresh connection per use; rebuilds the DB file first if missing."""
    db_file = ensure_db(path)
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def audit(conn: sqlite3.Connection, actor: str, action: str, detail: str = "") -> None:
    conn.execute("INSERT INTO audit_log (actor,action,detail) VALUES (?,?,?)",
                 (actor, action, detail))
