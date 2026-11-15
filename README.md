# Espoo Work Map

**Recruitment events where employers bring a real need, talent brings what they have actually done, and every conversation ends with an answer.**

Team **ScoobaNi** · Junction 2026 · City of Espoo challenge *Rethinking Recruitment*

**Live demo:** https://express-oboe-jx34fft.tmp.now/ (synthetic data; use the yellow demo bar)

---

## The problem

CVs are increasingly written by AI and screened by AI, so companies and job seekers talk to each other through machine-generated text. At the City of Espoo's recruitment events (TalentMatch, Työnantajatreffit):

- employers describe their needs **late and vaguely**, often only on the event day;
- talent struggles to show **what they can actually do**;
- language and degree requirements act as gates without saying what they are for;
- the City sees many registrations but **little signal and no visible follow-up**.

Espoo has about 19,000 unemployed people and about 650 open job ads, so employers' time at an event is the scarcest resource.

## What we built

One time-driven loop for both sides, for in-person and online events:

**Register → Choose → Your plan → Event day → Answers**

| Stage | Employer | Talent |
|---|---|---|
| Before | Writes a **need card** before a deadline: what the person does in the first weeks, at most 3 must-haves *each with a reason*, what we will teach, languages as *task + CEFR level*. A wording checker blocks discriminatory or vague requirements. | Registers with **3 things I have done**, in their own words and any language. No CV. |
| Choose | Sees **anonymous cards** (no name, country, photo, school, age) in random order and invites up to their number of talk slots. | Picks up to **5 employers**, one card at a time, and ticks which must-haves they meet. |
| Match | When interest is mutual, a 10-minute talk is booked automatically. | Gets a **personal plan**: times, booths on a venue map with a route, and *How to prepare* tips built from each employer's must-haves. |
| Event day | Scans the talent's QR pass, opens their profile and records **what they actually saw** the person do. | **Now / Next** screen with countdowns; online events have Jitsi video talks, a stage, virtual booths with Q&A and a networking lounge. |
| After | Must answer every talk within **7 days**, with a concrete next step (interview, work try-out, call) or a reason. | Confirms the next step or asks for another time. "Seen at the event" records and badges can be shared in later applications instead of a CV. |

The **City organizer** sees which need cards are on time, late or missing (with reminders and "write it with them by phone"), a live booth board on the day, and a report with outcome numbers and a **fairness panel**.

## Responsible by design

- **People decide, not AI.** Matching is deterministic rules and mutual choice; nobody is scored or ranked. AI (optional, NVIDIA Nemotron via NVIDIA Build) only restructures text a person wrote, and the person accepts or edits the result. Everything works without AI.
- **No bias inputs before the meeting.** Employers see no name, nationality, photo, education, age or career dates on cards. Card order is random. Only skill recognitions ("solved the task at the booth") appear on cards; attendance and hiring badges never affect matching, so first-timers are not disadvantaged.
- **Fairness is measured.** Outcome rates by registration language, shown only for groups of 10 or more people.
- **Privacy.** Contact details are shown only after the person shows their pass, and only the fields they chose to share. Badges are positive only and the person can hide any of them.
- **Synthetic data only.** Every person, company, job and event in this repository is fictional.

## Try the demo (about 3 minutes)

The yellow bar at the top switches roles with one click and moves a **demo clock** through the event phases. Other employers are simulated; the demo employer is controlled by you.

1. **Reset demo** → **Jobseeker (Aino)** → open *Espoo TalentMatch — spring 2027* → register → choose 3–4 employers.
2. **Matching closed** → Aino's plan: matched talks, preparation tips, venue map with her route.
3. **Event day** → Now/Next card and QR pass. As **Employer (Sanna)**: enter Aino's visitor number, record what you saw and propose a next step.
4. **After the event** → Aino sees answers with concrete next steps and confirms one.
5. **Organizer (Leena)** → need-card status, event report and fairness panel.
6. Repeat on *Espoo TalentMatch Online* for video talks, the lobby, booth Q&A and the lounge.

Demo accounts (password `demo1234`): `aino@example.com` (job seeker), `sanna@example.com` (employer, in-person event), `liisa@example.com` (employer, online event), `advisor@example.com` (City organizer). Also on `/sign-in`.

Between events the app also offers a job map with verified working conditions, combining part-time jobs into one week, jobs from City procurement employment clauses, and a support/subsidy guide.

## Tech

| Part | Stack |
|---|---|
| Backend | Python, FastAPI, SQLite (schema in `db/schema.sql`, synthetic seed in `db/seed/`) |
| Frontend | React, TypeScript, Vite, Tailwind CSS, Leaflet (OpenStreetMap), QR codes |
| Optional services | NVIDIA Build (Nemotron) for text help, Digitransit (HSL) for commute times, Jitsi Meet for online talks |
| Languages | UI in 10 languages spoken in Espoo (en, fi, sv, ru, ar, et, zh, fa, sq, uk), right-to-left for Arabic and Farsi |
| Accessibility | Keyboard support, large text, high contrast, easier reading, read-aloud |
| Tests | 250+ pytest tests (`python -m pytest -q`) |

## Run locally

Requires Python 3.13+ and Node.js 22+.

```bash
pip install -r requirements.txt
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

```bash
cd app/web
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

Open http://127.0.0.1:5173. Optional keys go in a git-ignored `.env` file at the repo root:

```
NVIDIA_API_KEY=...
DIGITRANSIT_API_KEY=...
```

Without them, AI help and commute times are hidden; everything else works.

## Deploy

One Docker container serves the API and the built frontend from the same origin.

```bash
docker build -t ewm .
docker run --rm -p 8080:8000 -e DEMO_MODE=1 ewm        # http://127.0.0.1:8080
docker run --rm -p 8080:8000 --env-file .env ewm        # with optional keys
```

**Render:** New → Blueprint → select this repository → enter the optional keys → Apply (`render.yaml`). The database is rebuilt from the seed on every start. On the free plan the service sleeps after about 15 minutes idle; the first request then takes 30–60 seconds.

## Repository

| Path | Contents |
|---|---|
| `app/api/` | FastAPI backend (routers, rules, wording checker, demo clock) |
| `app/web/` | React frontend |
| `db/` | Schema and synthetic seed data |
| `scripts/` | Seed generators and helpers |
| `tests/` | Backend tests |
| `docs/00-challenge/` | The original challenge brief |
| `docs/01-research/` | Research: Espoo context, AI in hiring, regulation, current Espoo events, pro-employment practices in other cities |
| `docs/02-ideation/` | Multi-agent ideation rounds |
| `docs/03-product/` | Specifications; the current one is [event-mode-spec.md](docs/03-product/event-mode-spec.md) |
| `docs/04-pitch/` | Pitch deck and submission texts; rebuild the deck with the `/pitch-deck` skill (`.devin/skills/pitch-deck/`) |
| `docs/decisions/` | [Decision log](docs/decisions/decision-log.md) |

Key reading: [challenge brief](docs/00-challenge/challenge-brief.md) · [how Espoo events work today](docs/01-research/10-espoo-events-today.md) · [Espoo labour market 2026](docs/01-research/08-espoo-local-situation-2026.md) · [regulation](docs/01-research/03-regulatory-fact-sheet.md) · [pitch deck](docs/04-pitch/presentation.pdf)
