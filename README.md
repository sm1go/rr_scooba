# rr_scooba — Rethinking Recruitment (Junction x City of Espoo)

Working repository of our Junction hackathon team for the **City of Espoo** challenge
**"Rethinking Recruitment"**: how can Espoo's recruitment and matchmaking events help companies
and talent find relevant, genuine connections when CVs are AI-written and screening is AI-assisted?

> North star (from the brief): *stronger signal and less noise* throughout registering for,
> attending and following up on an event.

## Status

| Phase | State |
|---|---|
| 0. Challenge intake | Done — brief + indexed stakeholders / pain points / constraints / judging criteria |
| 1. Research & problem analysis | Done — 7 notes incl. Junction tech partners and prior art |
| 2. Multi-agent ideation (3 rounds) | Done — 58 raw ideas → 20 consolidated features → final vote |
| 3. Feature catalog & shortlist | Done — *TalentMatch Signal* selected for the first prototype |
| 4. MVP build (`app/` + `db/`) | **Espoo Work Map (v2)** rebuilt per `docs/03-product/app-v2-spec.md`; v1 preserved in git tag `demo-v1` |

## Timeline (Junction 2026, Europe/Helsinki)

| When | What |
|---|---|
| Sat 14 Nov 12:00 | Submissions open on the Junction Platform |
| Sun 15 Nov 10:00 | **Final submission** (hard deadline) |
| Sun 15 Nov 14:00 | Final ceremony — challenge winners at 15:10 |

## Repository map

| Path | Contents |
|---|---|
| `docs/00-challenge/` | Original challenge brief (verbatim) + working index (S/P/C/J IDs) |
| `docs/01-research/` | Research and problem analysis: context, regulation, market, data sources |
| `docs/02-ideation/` | Multi-agent ideation: method, Round 1 proposals, Round 2 cross-reviews, Round 3 votes |
| `docs/03-product/` | Consolidated feature catalog, scoring outputs, shortlist |
| `docs/decisions/` | Decision log |
| `app/` | Application code — Espoo Work Map v2 (`app/api` FastAPI, `app/web` React) |
| `db/` | Database schema, migrations, synthetic seed data |
| `scripts/` | Helper scripts (e.g. score aggregation) |
| `AGENTS.md` | Working agreement and conventions for the team and AI agents |

## Key documents

- [Challenge brief](docs/00-challenge/challenge-brief.md) · [Tech challenges (stackable)](docs/00-challenge/tech-challenges.md)
- Research: [Espoo & TalentMatch](docs/01-research/01-context-espoo-and-talentmatch.md) · [AI in hiring](docs/01-research/02-ai-in-hiring-evidence.md) · [Regulation](docs/01-research/03-regulatory-fact-sheet.md) · [Market & data](docs/01-research/04-market-and-data-sources.md) · [Junction tech partners](docs/01-research/05-junction-2026-tech-partners.md) · [Prior art](docs/01-research/06-prior-art-open-source.md) · [Espoo mentor validation](docs/01-research/07-espoo-mentor-validation.md) · [Espoo labour market 2026](docs/01-research/08-espoo-local-situation-2026.md) · [Pro-employment trends](docs/01-research/09-pro-employment-trends.md)
- [Ideation method](docs/02-ideation/README.md) · [Round 1 digest — all 58 raw ideas](docs/02-ideation/round-1-digest.md) · [Round 2 brief](docs/02-ideation/round-2-brief.md)
- Product: [Feature catalogue F01–F20](docs/03-product/feature-catalog.md) · [Shortlist & MVP](docs/03-product/shortlist.md) · [Architecture](docs/03-product/architecture.md) · [Scoring](docs/03-product/scoring/summary.md)
- Build contract: [App v2 spec (authoritative)](docs/03-product/app-v2-spec.md) · [API contract pointer](docs/03-product/api-contract.md) · [Finnish-style design guide](docs/03-product/design-guide.md)
- [Decision log](docs/decisions/decision-log.md)

## Run the demo locally

Requires Python and Node.js. In separate terminals:

```bash
pip install -r requirements.txt
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd app/web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open `http://127.0.0.1:5173`. The app uses synthetic data only and no AI —
all matching is deterministic rules from the spec.

Demo accounts (password `demo1234`): `aino@example.com` (student),
`pekka@example.com` (retiree), `amira@example.com` (access needs),
`sanna@example.com` (employer), `advisor@example.com` (city advisor Leena).
A demo panel on `/sign-in` logs in as any of them with one tap.
