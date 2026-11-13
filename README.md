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
| 1. Research & problem analysis | In progress — 6 notes incl. Junction tech partners and prior art |
| 2. Multi-agent ideation (3 rounds) | Round 1 done (58 raw ideas) · Round 2 cross-review running |
| 3. Feature catalog & shortlist | Next |
| 4. MVP build (`app/` + `db/`) | Not started — waiting for the scope decision |

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
| `app/` | Application code (MVP) |
| `db/` | Database schema, migrations, synthetic seed data |
| `scripts/` | Helper scripts (e.g. score aggregation) |
| `AGENTS.md` | Working agreement and conventions for the team and AI agents |

## Key documents

- [Challenge brief](docs/00-challenge/challenge-brief.md)
- Research: [Espoo & TalentMatch](docs/01-research/01-context-espoo-and-talentmatch.md) · [AI in hiring](docs/01-research/02-ai-in-hiring-evidence.md) · [Regulation](docs/01-research/03-regulatory-fact-sheet.md) · [Market & data](docs/01-research/04-market-and-data-sources.md) · [Junction tech partners](docs/01-research/05-junction-2026-tech-partners.md) · [Prior art](docs/01-research/06-prior-art-open-source.md)
- [Ideation method](docs/02-ideation/README.md) · [Round 1 digest — all 58 raw ideas](docs/02-ideation/round-1-digest.md) · [Round 2 brief](docs/02-ideation/round-2-brief.md)
- [Decision log](docs/decisions/decision-log.md)
