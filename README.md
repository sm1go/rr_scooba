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
| 1. Research & problem analysis | In progress |
| 2. Multi-agent ideation (3 rounds) | In progress |
| 3. Feature catalog & shortlist | Next |
| 4. MVP build (`app/` + `db/`) | Not started — waiting for the scope decision |

## Repository map

| Path | Contents |
|---|---|
| `docs/00-challenge/` | Original challenge brief (verbatim) + working index (S/P/C/J IDs) |
| `docs/01-research/` | Research and problem analysis: context, regulation, market, data sources |
| `docs/02-ideation/` | Multi-agent ideation: method, Round 1 proposals, Round 2 cross-reviews, Round 3 votes |
| `docs/03-product/` | Consolidated feature catalog, scoring outputs, shortlist |
| `docs/decisions/` | Decision log |
| `app/` | Application code (MVP) |
| `db/` | Database schema, migrations, synthetic seed data |
| `scripts/` | Helper scripts (e.g. score aggregation) |
| `AGENTS.md` | Working agreement and conventions for the team and AI agents |

## Key documents

- [Challenge brief](docs/00-challenge/challenge-brief.md)
- [Ideation method](docs/02-ideation/README.md)
- [Decision log](docs/decisions/decision-log.md)
