# app/api — Espoo Work Map backend

FastAPI + SQLite backend for **Espoo Work Map** (v2), the City of Espoo
recruitment application. API is defined by
`docs/03-product/app-v2-spec.md` section 3 — that spec is authoritative.
Dev server `http://127.0.0.1:8000`, CORS open for the Vite dev server
`http://127.0.0.1:5173`. No AI in v2 — everything is deterministic rules.

## Run

```bat
pip install -r requirements.txt
python scripts/generate_synthetic.py   :: once — writes db/seed/*.json
uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

The SQLite file `db/talentmatch.sqlite` is rebuilt from `db/schema.sql` +
`db/seed/*.json` on startup when missing or when `PRAGMA user_version` is
stale (override path with env `TM_DB_PATH`).

## Layout

| File | Role |
|---|---|
| `main.py` | FastAPI app, CORS, lifespan bootstrap, routers |
| `db.py` | sqlite3 access, schema + seed loader, `SCHEMA_VERSION` rebuild, new ids, audit helper |
| `models.py` | Pydantic request models (spec section 3 shapes) |
| `auth.py` | scrypt password hashing, session tokens, `current_user`/`optional_user` deps |
| `serialize.py` | Shared serializers — job + conditions + labels, application, help request |
| `rules/labels.py` | Derived labels table, availability fit (every shift inside a selected slot, `schedule_flexible` always fits), haversine distance |
| `rules/lint.py` | Job wording check — protected/biased wording (incl. age) + suggestions, `blocking_issues` for publish |
| `routers/` | `catalog` (public catalog + event), `jobs` (public list/detail + employer/advisor write + wording + condition checks), `auth` (register/login/logout/me/profile/export/delete), `resident` (saved, applications, help requests), `employer` (company, own jobs, applications, status), `advisor` (help queue, employers, apply-for, overview, audit) |

## Rules that matter

- Public job output is identical for anonymous and signed-in callers.
- A missing `job_condition` row serializes as `unknown` ("Not known yet");
  employer edits preserve advisor verification unless the value changes.
- No response contains score/rank/rating keys; no age requirements anywhere.
- `needs` never leave the resident's own endpoints; only `shared_needs`
  chosen per application reach the employer.
- Max 5 active applications; duplicates → 409; status changes require a
  human-written `status_note`.

Demo accounts (password `demo1234`): `aino@`, `pekka@`, `amira@`,
`sanna@` (employer), `advisor@` (Leena) — all `@example.com`.
