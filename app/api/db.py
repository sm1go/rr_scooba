"""SQLite access: connect, schema, seed loading.

`db/talentmatch.sqlite` is a build artifact (git-ignored). It is rebuilt from
`db/schema.sql` + `db/seed/*.json` on startup whenever the file is missing or
its `PRAGMA user_version` is older than SCHEMA_VERSION (synthetic data only —
rebuilds are safe). The seed itself is regenerated via
`scripts/generate_synthetic.py` if absent. Override the path with the env var
`TM_DB_PATH` (used by tests).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB_DIR = ROOT / "db"
DEFAULT_DB = DB_DIR / "talentmatch.sqlite"
SCHEMA_SQL = DB_DIR / "schema.sql"
SEED_DIR = DB_DIR / "seed"
GENERATOR = ROOT / "scripts" / "generate_synthetic.py"
SCHEMA_VERSION = 8

SEED_REQUIRED = [
    "event.json", "employers.json", "jobs.json", "users.json",
    "applications.json", "help_requests.json", "saved_jobs.json",
    "procurement.json",
]

DEMO_PASSWORD = "demo1234"   # seeded demo accounts; documented in READMEs


def db_path() -> Path:
    return Path(os.environ.get("TM_DB_PATH", str(DEFAULT_DB)))


def _load_seed(name: str, seed_dir: Path):
    return json.loads((seed_dir / name).read_text(encoding="utf-8"))


def _load_opt(name: str, seed_dir: Path) -> list:
    p = seed_dir / name
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else []


def _run_generator() -> None:
    spec = importlib.util.spec_from_file_location("generate_synthetic", GENERATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load seed generator at {GENERATOR}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.main()


def ensure_db(path: Path | None = None) -> Path:
    """Create + seed the database file if it does not exist or is an older
    schema version. Returns the path."""
    path = path or db_path()
    if path.exists():
        with closing(sqlite3.connect(path)) as conn:
            version = conn.execute("PRAGMA user_version").fetchone()[0]
        if version >= SCHEMA_VERSION:
            return path
        path.unlink()                       # rebuild from schema + seed
    path.parent.mkdir(parents=True, exist_ok=True)

    missing_seed = any(not (SEED_DIR / f).exists() for f in SEED_REQUIRED)
    if missing_seed:
        _run_generator()

    now = datetime.now(timezone.utc)
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
        "INSERT INTO event (id,name,date,venue,advisor_note)"
        " VALUES (:id,:name,:date,:venue,:advisor_note)", ev)

    # employers_unlisted.json: small firms with no job on the map yet
    # (hidden-vacancy call list); hand-written, not from the generator
    for e in (_load_seed("employers.json", seed_dir)
              + _load_opt("employers_unlisted.json", seed_dir)):
        conn.execute(
            "INSERT INTO employer (id,name,about,contact_name,contact_email,"
            "contact_phone) VALUES (:id,:name,:about,:contact_name,"
            ":contact_email,:contact_phone)", e)
        if e.get("booth"):
            conn.execute(
                "INSERT INTO employer_event (employer_id,event_id,booth)"
                " VALUES (?,?,?)", (e["id"], ev["id"], e["booth"]))

    for j in _load_seed("jobs.json", seed_dir):
        confirmed = (now - timedelta(days=j.get("confirmed_days_ago", 0))).date()
        conn.execute(
            "INSERT INTO job (id,employer_id,title,field,duties,address,district,"
            "lat,lon,work_mode,pay_amount,pay_unit,pay_note,shifts,"
            "schedule_flexible,hours_min,hours_max,contract,experience,"
            "experience_note,qualifications,onboarding,languages,lifting,"
            "apply_question,cv_required,commitments,positions,status,source,"
            "contract_id,break_min,rota,confirmed_at)"
            " VALUES (:id,:employer_id,:title,:field,:duties,:address,:district,"
            ":lat,:lon,:work_mode,:pay_amount,:pay_unit,:pay_note,:shifts,"
            ":schedule_flexible,:hours_min,:hours_max,:contract,:experience,"
            ":experience_note,:qualifications,:onboarding,:languages,:lifting,"
            ":apply_question,:cv_required,:commitments,:positions,:status,"
            ":source,:contract_id,"
            ":break_min,:rota,:confirmed_at)",
            {**j,
             "duties": json.dumps(j.get("duties", []), ensure_ascii=False),
             "shifts": json.dumps(j.get("shifts", []), ensure_ascii=False),
             "qualifications": json.dumps(j.get("qualifications", []),
                                          ensure_ascii=False),
             "languages": json.dumps(j.get("languages", []), ensure_ascii=False),
             "confirmed_at": confirmed.isoformat(),
             "commitments": json.dumps(j.get("commitments", []),
                                       ensure_ascii=False),
             "contract_id": j.get("contract_id"),
             "break_min": j.get("break_min", 0),
             "rota": int(j.get("rota", 0))})
        _write_conditions(conn, j["id"], j.get("conditions", {}), "employer")

    from . import auth as auth_mod
    for u in _load_seed("users.json", seed_dir):
        conn.execute(
            "INSERT INTO user (id,email,phone,password_hash,role,name,"
            "employer_id) VALUES (?,?,?,?,?,?,?)",
            (u["id"], u.get("email"), u.get("phone"),
             auth_mod.hash_password(u.get("password") or DEMO_PASSWORD),
             u["role"], u.get("name", ""), u.get("employer_id")))
        profile = u.get("profile")
        if profile:
            _write_profile(conn, u["id"], profile)

    for a in _load_seed("applications.json", seed_dir):
        created = now - timedelta(days=a.get("days_ago", 0))
        conn.execute(
            "INSERT INTO application (id,job_id,user_id,name,contact_method,"
            "contact_value,availability_note,answer,cv_text,shared_needs,"
            "meet_at_event,status,status_note,created_by_advisor,created_at,"
            "updated_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (a["id"], a["job_id"], a.get("user_id"), a["name"],
             a.get("contact_method", ""), a.get("contact_value", ""),
             a.get("availability_note", ""), a["answer"], a.get("cv_text"),
             json.dumps(a.get("shared_needs", []), ensure_ascii=False),
             int(a.get("meet_at_event", 0)), a["status"],
             a.get("status_note", ""), int(a.get("created_by_advisor", 0)),
             created.isoformat(), created.isoformat()))

    for h in _load_seed("help_requests.json", seed_dir):
        created = now - timedelta(days=h.get("days_ago", 0))
        conn.execute(
            "INSERT INTO help_request (id,user_id,name,contact_method,"
            "contact_value,job_id,kind,condition_keys,message,consent,status,"
            "advisor_id,advisor_reply,created_at,updated_at)"
            " VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (h["id"], h.get("user_id"), h.get("name", ""),
             h.get("contact_method", ""), h.get("contact_value", ""),
             h.get("job_id"), h["kind"],
             json.dumps(h.get("condition_keys", []), ensure_ascii=False),
             h.get("message", ""), int(h.get("consent", 0)), h["status"],
             h.get("advisor_id"), h.get("advisor_reply", ""),
             created.isoformat(), created.isoformat()))

    for c in _load_opt("procurement.json", seed_dir):
        conn.execute(
            "INSERT INTO procurement_contract (id,employer_id,title,"
            "value_eur,starts,ends,due,hires_required,hires_done,"
            "target_groups) VALUES (?,?,?,?,?,?,?,?,?,?)",
            (c["id"], c["employer_id"], c["title"], c.get("value_eur", 0),
             c["starts"], c["ends"], c["due"], c["hires_required"],
             c.get("hires_done", 0),
             json.dumps(c.get("target_groups", []))))

    # demo credentials: seen once by the seeded advisor, never a copy
    advisor_id = conn.execute(
        "SELECT id FROM user WHERE role='advisor' LIMIT 1").fetchone()
    advisor_id = advisor_id["id"] if advisor_id else None
    for uid, label in (("u-aino", "Hygiene passport (hygieniapassi)"),
                       ("u-pekka", "Driving licence C")):
        if conn.execute("SELECT 1 FROM user WHERE id=?", (uid,)).fetchone():
            conn.execute(
                "INSERT INTO credential (id,user_id,label,advisor_id,"
                "checked_at) VALUES (?,?,?,?,?)",
                (f"cred-{uid}", uid, label, advisor_id,
                 (now - timedelta(days=30)).date().isoformat()))

    for s in _load_seed("saved_jobs.json", seed_dir):
        conn.execute("INSERT OR IGNORE INTO saved_job (user_id,job_id)"
                     " VALUES (?,?)", (s["user_id"], s["job_id"]))

    _seed_event(conn, seed_dir, now)


def _seed_event(conn: sqlite3.Connection, seed_dir: Path,
                now: datetime) -> None:
    """Optional event-mode seed files (spec v3 §8)."""
    def opt(name: str):
        return _load_opt(name, seed_dir)

    for v in opt("event_visitors.json"):
        conn.execute(
            "INSERT OR IGNORE INTO event_visitor (user_id,event_id,code)"
            " VALUES (?,?,?)", (v["user_id"], v["event_id"], v["code"]))
    for p in opt("event_plan.json"):
        conn.execute(
            "INSERT OR IGNORE INTO event_plan (user_id,event_id,employer_id)"
            " VALUES (?,?,?)", (p["user_id"], p["event_id"], p["employer_id"]))
    for t in opt("event_talks.json"):
        talked = now - timedelta(days=t.get("days_ago_talked", 0))
        answered = (now - timedelta(days=t["days_ago_answered"])
                    if t.get("days_ago_answered") is not None else None)
        conn.execute(
            "INSERT OR IGNORE INTO event_talk (id,event_id,user_id,employer_id,"
            "status,outcome,employer_note,talked_at,answered_at)"
            " VALUES (?,?,?,?,?,?,?,?,?)",
            (t["id"], t["event_id"], t["user_id"], t["employer_id"],
             t["status"], t.get("outcome"), t.get("employer_note", ""),
             talked.isoformat(),
             answered.isoformat() if answered else None))


def _write_profile(conn: sqlite3.Connection, user_id: str, p: dict) -> None:
    conn.execute(
        "INSERT INTO resident_profile (user_id,contact_method,district,fields,"
        "availability,max_hours_per_week,needs,languages,about)"
        " VALUES (?,?,?,?,?,?,?,?,?)",
        (user_id, p.get("contact_method"), p.get("district"),
         json.dumps(p.get("fields", []), ensure_ascii=False),
         json.dumps(p.get("availability", []), ensure_ascii=False),
         p.get("max_hours_per_week"),
         json.dumps(p.get("needs", []), ensure_ascii=False),
         json.dumps(p.get("languages", []), ensure_ascii=False),
         p.get("about", "")))


def _write_conditions(conn: sqlite3.Connection, job_id: str,
                      conditions: dict, source: str) -> None:
    for key, val in conditions.items():
        if isinstance(val, dict):
            value, note = val.get("value"), val.get("note", "")
        else:
            value, note = val, ""
        if value not in ("yes", "no"):
            continue                      # 'unknown' = simply no row
        conn.execute(
            "INSERT OR REPLACE INTO job_condition (job_id,key,value,source,"
            "checked_at,note) VALUES (?,?,?,?,?,?)",
            (job_id, key, value, source,
             datetime.now(timezone.utc).date().isoformat(), note))


def connect(path: Path | None = None) -> sqlite3.Connection:
    """Fresh connection per use; rebuilds the DB file first if needed."""
    db_file = ensure_db(path)
    # anyio may run the dependency's setup and teardown on different
    # worker threads; each request still owns its connection exclusively.
    conn = sqlite3.connect(db_file, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_conn():
    """FastAPI dependency: one connection per request, closed on exit."""
    conn = connect()
    try:
        yield conn
    finally:
        conn.close()


def audit(conn: sqlite3.Connection, actor: str, action: str,
          detail: str = "") -> None:
    conn.execute("INSERT INTO audit_log (actor,action,detail) VALUES (?,?,?)",
                 (actor, action, detail))


def new_id(conn: sqlite3.Connection, prefix: str) -> str:
    """Short sequential id: ap-101, job-061, ... — takes the max numeric
    suffix, ignoring slug ids like 'job-cafe-weekend'."""
    table = {"ap": "application", "job": "job", "hr": "help_request",
             "u": "user", "emp": "employer", "et": "event_talk",
             "cred": "credential", "hire": "contract_hire"}[prefix]
    n = 0
    for r in conn.execute(
            "SELECT id FROM {} WHERE id LIKE ?".format(table),
            (f"{prefix}-%",)).fetchall():
        tail = r["id"].rsplit("-", 1)[1]
        if tail.isdigit():
            n = max(n, int(tail))
    return f"{prefix}-{n + 1:03d}"
