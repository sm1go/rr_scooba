# app/api — TalentMatch Signal backend

FastAPI backend for the MVP. Implements `docs/03-product/api-contract.md` v1
exactly: all endpoints under `/api`, dev server `http://127.0.0.1:8000`, CORS
open for the Vite dev server `http://127.0.0.1:5173`.

## Run

```bat
pip install -r requirements.txt
python scripts/generate_synthetic.py   :: once — writes db/seed/ + db/esco/
uvicorn app.api.main:app --reload      :: serves http://127.0.0.1:8000/api
```

The SQLite file `db/talentmatch.sqlite` is rebuilt from `db/schema.sql` +
`db/seed/*.json` on startup whenever missing (override with env `TM_DB_PATH`).

## Layout

| File | Role |
|---|---|
| `main.py` | FastAPI app, CORS, lifespan (env + DB bootstrap), routers |
| `db.py` | sqlite3 access, schema + seed loader, card (de)serialisation, audit helper |
| `models.py` | Pydantic models mirroring the contract's shared types |
| `llm.py` | LLM adapter (mock / nvidia / gemma) + the three AI suggestion flows |
| `rules/lint.py` | F02 rulebook — max 5 hints, law + rewrite + pool before/after |
| `rules/pool.py` | F03 k-anonymous pool bands (k = 10) + per-must-have elasticity |
| `rules/sparks.py` | F06 budget formula, refund paths, reveal-on-accept, first free slot |
| `rules/quote_guard.py` | F04 "no quote, no claim" + verb-inflation refusal |
| `rules/closure.py` | F13 reason-chip validation, message builder, F14 support banner |
| `routers/` | Endpoint groups: `company`, `talent`, `sparks`, `organiser` |

## LLM providers

`LLM_PROVIDER` = `mock` (default + fallback) | `nvidia` | `gemma`, loaded from
`.env` (git-ignored — never commit it). `.env` is parsed by `llm.load_env()`;
no secrets live in code.

- `nvidia` → `https://integrate.api.nvidia.com/v1`, model
  `nvidia/nemotron-3.5-super-vl-120b-a12b`, key `NVIDIA_API_KEY`.
- `gemma` → `GEMMA_BASE_URL` + `/chat/completions`, model `GEMMA_MODEL`.
- `mock` → recorded outputs in `db/seed/recorded/`.

Any remote failure falls back to `mock` and the response's `provider` says so.
`POST /api/compiler/draft` always produces its `trace`
(`esco_search → lint_requirements → pool_preview → submit_card`) by really
running the deterministic tools — mock mode included.

## Guarantees

- No endpoint returns a score, rank or ordered list of people (test-enforced).
- Pool counts are bands only ("fewer than 10", "10–19", "20–49", "50+").
- Names are revealed only after a Spark is accepted; declined and
  deadline-expired Sparks are refunded.
- Every AI suggestion and every human approval lands in `audit_log`
  (`GET /api/audit`, last 50).

## Tests

```bat
python -m pytest -q
```

## Prototype boundary

This is a synthetic-data demo, not a deployable recruitment service. It has no
user authentication or authorization; IDs and role screens are demo fixtures.
Never put real candidate or employer data into it. Before any pilot, add
identity-bound access control, retention/deletion workflows, privacy review,
and an approved hosting/data-processing setup.
