# AGENTS.md — working agreement & conventions

Applies to every human and AI agent working in this repository.

## Project

- Junction hackathon — City of Espoo challenge "Rethinking Recruitment".
- Event: Junction 2026 (13–15 Nov 2026, Espoo). **Final submission Sun 15 Nov 10:00** Europe/Helsinki; submissions open Sat 14 Nov 12:00. Tech-partner challenges can be stacked on top of the Espoo track.
- Remote: https://github.com/sm1go/rr_scooba (branch `main`). Local working copy: `C:\Users\kacpe\OneDrive\Pulpit\junction`.

## Owner's working agreement

1. Everything related to the project lives here: research, analyses, decisions, code and database.
2. Keep it well catalogued: put material in the right folder (map in `README.md`) and keep `README.md` as the index.
3. The AI assistant acts in every startup role that is needed (strategy, product, design, engineering, responsible AI & legal, domain expertise, pitch).
4. Commit early and often, and push to `origin/main`.

## Layout rules

- Numbered `docs/` folders follow the project phases: `00-challenge` -> `01-research` -> `02-ideation` -> `03-product`.
- New research note -> `docs/01-research/<topic>.md`. New decision -> append a row to `docs/decisions/decision-log.md`.
- Code -> `app/`. Schema, migrations, seed data -> `db/`. Helper scripts -> `scripts/`.

## Conventions

- Repository content in **English** (jury, mentors and Junction audience are international); conversation with the owner in Polish.
- Stable IDs: stakeholders S1–S3, pain points P1–P10, constraints C1–C6, judging criteria J1–J3 (defined in `docs/00-challenge/challenge-brief.md`). Raw ideas: `<ROLE>-NN` (STR, PM, UX, TECH, RAI, TAL). Consolidated features: `F01…`.
- Scoring: integers 1–5 per criterion; weighted = 0.45·J1 + 0.35·J2 + 0.20·J3 (official judging weights). Only peer scores are aggregated.
- **Synthetic data only** (C2). Never commit real personal data or secrets (`.env*` is git-ignored).
- Commit messages: Conventional Commits (`docs:`, `feat:`, `fix:`, `data:`, `chore:`), imperative mood, one logical change per commit.
- Windows: shell commands longer than ~8 KB get truncated — write large files with an editor/file tool, not a heredoc.

## Tooling

- Python 3.14 (`python`) and Node 25 are available on the dev machine.
