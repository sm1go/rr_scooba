# Junction Platform submission — ScoobaNi

Text pasted into `hackjunction.app/participate/45/project`. Keep in sync with the platform.

## Project Name (max 30)

ScoobaNi

## Punchline (max 200)

Espoo Work Map: recruitment events where employers bring a real need, talent brings proof in their own words, and every talk ends with an answer. No CVs, no ranking, no bias inputs.

## Description (max 5000, markdown)

**Espoo Work Map** is a signal layer for the City of Espoo's recruitment events (TalentMatch and Työnantajatreffit), covering *before, during and after* the event day, in person and online.

### The problem
CVs are written by AI and screened by AI, so both sides talk through machine-generated text. Employers describe their needs late and vaguely, talent can't show what they can actually do, language becomes a gate with no reason given, and the City sees lots of registrations but little real signal and no visible follow-up. Espoo has ~19,000 unemployed people against ~650 open job ads, so employer time at events is the bottleneck.

### What we built: one time-driven loop
**Register → Choose → Your plan → Event day → Answers**

- **Need cards (employer).** Before a deadline the employer describes what the person will do in the *first week*, max 3 must-haves *each with a reason*, and every language need as a *task + CEFR level* ("Finnish B1 for customer phone calls"). A wording checker blocks vague or discriminatory requirements.
- **"3 things I have done" (talent).** No CV. Talent describes concrete things they have done, in their own words.
- **Choosing with hard limits.** Talent picks up to 5 employers, one card at a time; employers invite as many anonymous cards as they have slots. Mutual interest books a 1:1 talk automatically into a free slot.
- **Your plan.** A personal schedule plus a "How to prepare" list built from the employer's must-haves.
- **Event day.** A Now / Next screen, QR pass, venue map with the route; the employer scans the QR and notes what they actually *saw* at the talk.
- **Answers within 7 days.** Every talk ends with a concrete next step (interview, work try-out, call) or "not this time" with a reason. Answers become records the person can reuse.
- **Organiser view (City).** Need-card status (on time / late / missing) with reminders, a funnel (registered → chose → met → next step) and a fairness panel by registration language.
- **Online event.** The same loop with Jitsi video 1:1s that open 5 minutes before the slot, virtual employer booths with Q&A, a stage programme and a networking lounge.

### Responsible by design
- Before the meeting employers see **no name, country, photo, school, age or career dates**. Card order is random; nobody is ranked or scored.
- **AI only as a helper**: optional NVIDIA Nemotron (NVIDIA Build, OpenAI-compatible) restructures text the person wrote, the person accepts or edits it, every call is audited, and there is a rules-based fallback. All matching is deterministic rules.
- **Measured fairness**: outcome rates by registration language, with k-anonymity (groups under 10 show no rates).
- **Synthetic data only.** Badges are controlled by the person and never affect matching.

### Demo (3 minutes)
1. Sanna (employer) files her need card.
2. Aino (talent) registers with 3 things she has done and picks employers. Match!
3. Move the demo clock to "matching closed": her plan and preparation list.
4. Event day: Now/Next, scan the QR, Sanna notes what she saw.
5. After: Sanna proposes a work try-out, Aino replies "Yes, I'll come".
6. Leena (City) sees late need cards, the funnel and the fairness panel.

A built-in demo clock moves the event through its phases and simulates other employers; one click resets the synthetic data. Demo accounts (password `demo1234`): `aino@example.com`, `sanna@example.com`, `advisor@example.com`, or use the one-tap demo panel on `/sign-in`.

### Tech
Python FastAPI + SQLite (wording checker, slot scheduler, phase logic on one clock), React 19 + Vite + TypeScript + Tailwind, Leaflet maps, QR passes, multilingual UI. ~7.8k lines of Python, ~21k lines of TypeScript, 250+ pytest tests. Self-hostable stack that fits public-sector procurement.

### From hackathon to pilot
Runs next to existing TalentMatch and Työnantajatreffit events. Pilot one event and measure answers within 7 days and next steps per talk, by language group.

## Links

- Source Code: https://github.com/sm1go/rr_scooba
- Project Demo: _(public URL once deployed)_
- Video: _(link to recorded demo)_
- Other Link: https://github.com/sm1go/rr_scooba/blob/main/docs/04-pitch/presentation.html
- Presentation: PDF already uploaded on the platform

## Tech challenges

- Best Use of Nemotron (NVIDIA) — optional; Nemotron is a helper, not core, so fit is moderate.
