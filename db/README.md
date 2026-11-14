# db/

SQLite schema and **synthetic** seed data for Espoo Work Map (v2).
Never store real personal data here (constraint C2).

## Contents

| Path | Contents |
|---|---|
| `schema.sql` | v2 schema: `user`, `session`, `resident_profile`, `employer`, `event`, `employer_event`, `job`, `job_condition`, `saved_job`, `application`, `help_request`, `audit_log`. `PRAGMA user_version` bumps on each schema change — stale DBs are rebuilt automatically |
| `seed/*.json` | Generated demo world: 70 employers, 158 open jobs across 14 fields (60 base jobs from `generate_synthetic.py` + 98 from `gen_more_jobs.py`, incl. manufacturing/welding, health care and property maintenance), ~500 job conditions, the seeded event (31 jobs with booths), 5 demo users, applications, saved jobs, help requests — all synthetic |
| `seed/employers_unlisted.json` | Hand-written (not from the generator): three small firms with no job on the map, so the advisor's hidden-vacancy call list has entries |
| `talentmatch.sqlite` | Build artifact, **git-ignored**. Rebuilt from `schema.sql` + `seed/` on API startup whenever missing or stale |

## Rebuild

```bat
python scripts/generate_synthetic.py   :: regenerates seed/ (deterministic; 60 base jobs)
python scripts/gen_more_jobs.py        :: then appends 98 more jobs + 42 employers + 3 fields (idempotent)
del db\talentmatch.sqlite              :: optional; the API recreates it
uvicorn app.api.main:app --host 127.0.0.1 --port 8000
```

## Demo accounts (password `demo1234`)

| Login | Role | Persona |
|---|---|---|
| `aino@example.com` | resident | Student (weekend/summer work) |
| `pekka@example.com` | resident | Retiree (light part-time) |
| `amira@example.com` | resident | Job seeker with access needs |
| `sanna@example.com` | employer | Café employer with applications in her inbox |
| `advisor@example.com` | advisor | Leena, Employment Espoo |
