# db/

Database schema, **synthetic** seed data and the ESCO-like skill subset for the
TalentMatch Signal MVP. Never store real personal data here (constraint C2).

## Contents

| Path | Contents |
|---|---|
| `schema.sql` | SQLite schema: event, company, challenge_card, card_requirement, talent, talent_identity, evidence_card, evidence_claim, spark, meeting, conversation_tick, closure, audit_log |
| `esco/skills.json` | ~24 ESCO-*like* skills used by `esco_search`, pool counting and claim tagging. **URIs are placeholders** (marked in the file) — labels follow the ESCO style (CC BY 4.0) |
| `seed/*.json` | Generated demo world: `ev-2026-11`, 12 companies with approved cards, 300 talents (fictional names, CEFR languages, confirmed claims), Sparks in Lumo's inbox, a few meetings and one closure |
| `seed/recorded/*.json` | Recorded demo content for the mock LLM provider: Sanna's Lumo ad + compiled draft card, Amira's story + claims/refusals |
| `seed/twin_report.json` | F18 parity table — clearly marked **precomputed placeholder**, provider `mock` |
| `talentmatch.sqlite` | Build artifact, **git-ignored**. Rebuilt from `schema.sql` + `seed/` on API startup whenever missing |

## Rebuild

```bat
pip install -r requirements.txt
python scripts/generate_synthetic.py   :: regenerates seed/ + esco/ (deterministic, seeded)
del db\talentmatch.sqlite              :: optional; the API recreates it on startup
uvicorn app.api.main:app --reload
```

Demo anchors: company `co-lumo` (contact Sanna Virtanen, card `card-co-lumo`),
talent `ta-0427` ("Talent #0427" = Amira Haddad, fictional). The generator
prints the pool sanity numbers: trio+Finnish C2 must stay < 10 ("fewer than 10")
and trio+Finnish B1+ in 20–49 — that is the demo's "fluent → B1" pool moment.
