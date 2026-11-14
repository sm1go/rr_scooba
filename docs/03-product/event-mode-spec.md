# Event mode spec (v4): the app is built around City of Espoo recruitment events

Decision D014. Research: `docs/01-research/10-espoo-events-today.md`.

**Goal (from the brief):** stronger signal, less noise, before / during / after an event, without disadvantaging people for nationality, language, education, career path or other traits unrelated to the opportunity.

**Principles**
- Employers describe a real need **early**; the organizer can see and chase late ones.
- Talent shows **what they have done, in their own words**, plus facts a human has checked.
- Conversations are **booked by mutual interest** within hard limits, so nobody's time is wasted.
- Employers see **no name, country, photo, school, age or career dates** before the meeting. The card order is random and no person is ranked.
- AI only structures text the person wrote and the person approves it. It never scores.
- Every conversation ends with an answer; the organizer sees aggregate outcomes and a fairness panel.

## 1. Information architecture

- `/` = **Events hub**:
  - hero "Recruitment events by the City of Espoo";
  - cards for upcoming events (format chip, date, place, language, number of employers, the current phase: "Registration open" / "Needs published" / "Today" / "Finished");
  - a three-step explainer (Before · On the day · After) with role-specific calls to action;
  - secondary links to open jobs (`/jobs`), Combine jobs and Support.
- `/events/:id` = **event page** with phase tabs **Before · On the day · After**. All three are always clickable (demo); the default tab follows the date.
  - Public content: description, programme, the employers and their need cards. Need cards become public on `publish_date`; before that the page shows "N employers registered; needs published on <date>".
- The jobs list/map moves from `/` to `/jobs` (same page component). Every link that meant "jobs home" now points to `/jobs`. The old `/event` redirects to `/events/<main event id>`.
- Nav (resident/anonymous): **Events** · Jobs · Combine jobs · Saved · My applications · Profile · Support. Employer: **Events** · My jobs · Applications · Company. Advisor (organizer): **Events** · Requests · Jobs · Follow-up · City contracts · City support.
- Role homes after sign-in: everybody lands on `/`; employer and advisor event cards link to their own event workspaces.

## 2. Data model (schema v9)

- `event` gains:
  - `format` ('talentmatch' | 'treffit'), `language` ('en' | 'fi'), `starts_at`, `ends_at` (ISO datetimes), `address`, `description`;
  - `programme` (JSON list `{start, end, title, kind}`, kind in 'pitch', 'workshop', 'one_to_one', 'fair', 'presentation', 'walk_in');
  - `capacity` (talent places), `slot_minutes` (default 10);
  - `need_deadline` (date), `publish_date` (date);
  - `time_groups` (JSON list `{id, label, entry}`, e.g. A 14:30, B 15:30, C 16:30).
- `employer_event` gains:
  - `need_card` (JSON or NULL), `need_submitted_at`, `need_by` ('employer' | 'advisor');
  - `slots` (number of 1:1 meetings offered), `formats` (JSON subset of 'one_to_one', 'walk_in', 'pitch');
  - `reminders_sent` (int), `last_reminder_at`.
- **Need card** JSON:
  - `first_week`: 1–5 strings ("What will the person do in their first week?");
  - `must_haves`: max 3 items `{text, why}`, why required;
  - `will_teach`: list of strings;
  - `languages`: max 2 items `{name, level (CEFR), task}`;
  - `job_ids`: optional links to open jobs of that employer.
  
  The card is validated with the existing wording checker (`app/api/rules/lint.py`, same rules as job ads). Blocking issues → 422 with the issues listed.
- `talent_registration`:
  - `id, event_id, user_id, time_group, status` ('registered' | 'waitlist' | 'cancelled'), `card_language` (UI language at registration), `created_at`;
  - `card` JSON: `done` (1–3 items `{text, own_words}`), `looking_for`, `district`, `availability` (slots).
  - Capacity full → waitlist.
- `event_plan` (existing) becomes the talent's **interest** list:
  - max 5 employers per event (409 beyond);
  - gains `meets` (JSON indices of the employer's must-haves the person says they meet) and `language_levels` (JSON `{name: level}`).
- `event_invite`: `(event_id, employer_id, registration_id, created_at)`, the employer's interest in an anonymous card. Max invites = the employer's `slots`.
- `event_meeting`: `id, event_id, employer_id, user_id, starts_at, status` ('booked' | 'done' | 'no_show' | 'cancelled').
  - Created automatically when interest and invite are mutual.
  - Takes the earliest free slot inside the one_to_one programme window that is at or after the person's time-group entry and free for both sides.
  - No free slot → stays mutual with "we will offer a walk-in time" (organizer can place it).
- `event_talk` (existing) gains `meeting_id` and `observed` (JSON list of first_week items the employer saw the person do or explain concretely), plus the existing outcome/note.

## 3. Before the event

**Employer** (`/employer/events/:id`, tab Before)
- Registers for the event; chooses formats and the number of slots.
- Fills the need card with the three prompts and a live deadline line: "Due in 9 days (19 Feb)". It can link existing jobs.
- Sees anonymous talent cards. By default only people who chose them are shown, with an "everyone registered" toggle. Order is random but stable per employer.
- Each card shows the `done` items (own words, original language, plus a Translate button when AI is on), `looking_for`, which of *their* must-haves the person says they meet, the person's level for the language task, checked documents (labels only) and availability overlap.
- Invites, within the slot limit. Mutual interest → booked meeting, shown in a list.

**Talent** (`/events/:id`, tab Before)
- Registers: picks a time group; writes "3 things I have done" from guided prompts (any language, voice input).
  - Prompt examples: "Something you fixed or organised", "Something you did for a customer or a person", "Something you learned fast".
  - AI is optional: "Help me write this clearly" restructures the text into one short line per item and keeps the original as `own_words`. The person must accept or edit it.
- Browses need cards; picks up to 5 employers, ticks which must-haves they meet and their level for each language task. The page shows why an employer fits: hours/area match, must-haves met, language task level.
- Sees booked meetings and the waitlist status.

**Organizer** (advisor; `/advisor/events/:id`, tab Before)
- Employers table: need card status (submitted on time / late / missing with days to deadline), slots, invites used. Actions:
  - "Send reminder": simulated, increments counter, audit only, no real message;
  - "Call": tel: link;
  - "Fill in with them by phone": opens the need-card form as the advisor, saved with `need_by='advisor'`.
- Talent numbers by time group, waitlist count, mutual matches and booked meetings.

## 4. On the day

- **Talent "My day"** (tab On the day):
  - big visitor code;
  - entry time of the time group;
  - timeline of booked meetings (time, booth, employer, one-line need);
  - booths with "join the walk-in queue" (simple FIFO per booth).
- **Employer booth view:**
  - today's meetings in order, with the next person's anonymous card 2 minutes before;
  - enter the visitor code → the name appears;
  - after the talk, tick `observed` items from their first_week list and choose next step / not now with a note (existing rule: note required);
  - mark no-show.
- **Organizer live board:** per booth now/next, no-shows, free slots, walk-in queues. "Offer the free slot" books the first person in that booth's walk-in queue.

## 5. After the event

- **Talent:** answers from every conversation (existing), and a **"Seen at the event"** record per talk: employer, date, observed items. The person can share it in applications, as a snapshot (like checked documents).
- **Employer:** list of talks still needing an answer, 7-day rule (existing follow-up for advisors).
- **Organizer report:**
  - per booth: meetings booked, held, no-shows, next steps;
  - need cards on time %;
  - answers within 7 days %;
  - **fairness panel**: by registration language (`card_language`), count registered → chose employers → invited → met → next step, with rates. Groups under 10 people show "fewer than 10" and no rate. A plain note explains how to read gaps ("If a group meets the same must-haves but is invited less often, talk to the employers about their requirements").

## 6. Demo data (synthetic, names clearly fictional, events marked "(demo)")

- **E1 "Espoo TalentMatch — spring 2027 (demo)"**:
  - English, 19 Mar 2027, 13:00–17:30, Otaniemi (demo venue);
  - programme like the real 2025 edition (pitching, transferable-skills workshop, 1:1 meetings 14:30–17:30, job fair, explore fair);
  - capacity 300; time groups A 14:30 / B 15:30 / C 16:30; need deadline 19 Feb 2027; publish 5 Mar 2027.
  - 12 employers: 9 need cards submitted (2 of them late), 3 missing.
  - About 40 synthetic talent registrations with varied cards. Card languages are spread so at least 3 groups have ≥ 10 people (e.g. en, fi, ru, ar, uk).
  - Some interests, invites and booked meetings.
  - Some talks already recorded with observed items and outcomes, so the On the day and After tabs have content.
  - Aino, Pekka and Amira are registered with cards; Sanna's company is a registered employer with a need card; Leena is the organizer.
- **E2 "Työnantajatreffit at Sello library (demo)"**: Finnish, walk-in interview format, 26 Nov 2026 12:00–15:00. It is the current single event migrated, with its existing employers, plans and talks.

## 7. People first: personal QR pass, badges, networking (v5, decision D015)

**Tagline:** "From people, for people" (fi "Ihmisiltä ihmisille"). It is shown in the home hero, above the unchanged three-line How it works (Before / On the day / After). Under it a short line: "You choose employers by what they need. Employers choose you by what you have done. You meet when it is mutual." AI stays a small optional helper: the "Help me write this clearly" button becomes a quiet text link, and nothing in matching, cards or badges uses AI.

**7.1 Personal QR pass**
- Every registered talent and every employer representative of a joined employer gets a pass for each event.
  - Table `event_pass(token PK, event_id, user_id, created_at)`; the token is 22 url-safe random chars.
  - The QR encodes `<PUBLIC_BASE>/p/<token>` (same base logic as the paper notice).
- The pass screen (`/events/:id/pass`) has a large black-on-white QR, the person's first name, the event name and the 4-digit visitor number as a fallback for people without a phone. It also has a "Print my pass" button and a brightness tip.
  - It is reachable from My day, the event page and Profile.
- Showing your QR means you agree to share your event profile with the person who scans it. That is said in plain words on the pass screen.
- Scanning works in two ways:
  - the phone camera opens `/p/<token>`;
  - in the app, a "Scan" button uses BarcodeDetector where the browser supports it, otherwise "Use your phone camera, or type the visitor number".
- `GET /api/p/{token}` requires the viewer to be signed in and part of the same event: registered talent, a joined employer's user, or an advisor. Otherwise 403, with a sign-in prompt in the UI.
  - Every scan stores `event_scan(id, event_id, scanner_id, scanned_id, created_at)` and creates a connection.

**7.2 Event profile (what the scanner sees)**
- **Talent:**
  - first name and the contact fields the person chose to share (Profile settings: share email yes/no, share phone yes/no, optional link e.g. LinkedIn);
  - `looking_for` and the "things I have done";
  - checked documents;
  - visible badges;
  - visible "Seen at the event" records.
- **Employer representative:** name, company, the company's need card for that event, shared contact, company badges.
- **Employer scanning a talent** gets three actions:
  1. "Record a talk": opens/creates the `event_talk` for this pair, so the 7-day answer rule applies to QR talks too;
  2. "Give a badge";
  3. a private note for themselves (stored on the connection, never shown to the talent).

**7.3 Badges (positive only, the person controls visibility)**

Table `badge(id, user_id, employer_id NULL, event_id, kind, label, note, given_by, created_at, hidden 0/1)`.

| kind | Given by | Rule |
|---|---|---|
| `attended` | system | Once per event, when the person has a done meeting, a recorded talk or was scanned at the event |
| `kudos` | employer representative | Only to someone they met, talked to or scanned at that event. Label from a fixed list: explains_clearly, solved_task, customer_focus, team_player, learns_fast, reliable, helped_others. One label per employer per person per event; max 10 kudos per employer per event; optional note ≤ 140 chars, checked by the wording checker |
| `hired` | employer or advisor | For someone hired after an event conversation; one per employer–person pair |
| `organizer` | advisor | pitched, workshop, volunteer |
| `employer_answered` (company badge) | system | Employer answered every talk of an event within 7 days |

- **Where badges appear:**
  - the talent's own Profile ("My badges", each with Hide / Show);
  - the event profile after a scan;
  - in employer anonymous cards, **only kudos labels with counts**, e.g. "Solved the task at a booth ×2", because they are evidence of skill. Attended, hired and organizer badges never appear in anonymous cards and never affect order or matching, so newcomers are not at a disadvantage;
  - company badges on need cards.
- No negative badges and no ratings. Badge givers are named on the profile ("from Kahvila Koivu, TalentMatch spring 2027").

**7.4 Networking: connections**
- Any scan between two event participants creates a connection both ways: `connection(user_a, user_b, event_id, created_at, note_a, note_b)`, unique per pair and event. Talent-to-talent networking works the same way.
- "My connections" (Profile tab and the event After tab) lists the person, their role/company, the event and the contact they chose to share. Remove is allowed.
- The event After tab for talent shows "People you met" (connections) next to the answers and the Seen-at-the-event records.

**7.5 Demo data**
- Add a past event **E0 "Työnantajatreffit at Iso Omena — autumn 2026 (demo)"** (finished, 8 Oct 2026) with a few talks, so badges have history.
- Seed about 30 badges: attended for E0 participants, about 12 kudos from E0 employers, 2 hired, 2 organizer. Aino has attended + 2 kudos + organizer "pitched".
- Seed about 20 connections, including talent-to-talent ones.
- Passes for every E1 registration and E1 employer user.

## 8. Simplify: one loop, one next step, choose one card at a time (v6, decision D016)

The owner found the event pages overloaded: the solution was hard to see. The menu and other pages stay as they are. Only the event experience is simplified, and a demo bar is added.

**8.1 Steps instead of tabs (talent and employer).** A stepper at the top of the event page shows the person's own loop, with done steps ticked and the current one highlighted. Clicking a step shows its content.
- Talent: **1 Register → 2 Choose employers → 3 Meet → 4 Answers**.
- Employer: **1 Your need card → 2 Choose people → 3 Meet → 4 Answer everyone**.
- The organizer keeps the Before / On the day / After tabs.
- Anonymous visitors see the overview with the need cards and the sign-in call to action.
- Default step = the first step not done. Talent: not registered → 1; registered → 2 until the event day; on the event day → 3; after the event → 4. Employer: no need card → 1; card sent → 2; event day → 3; after → 4.

**8.2 "Your next step" card.** Always first under the stepper: one plain sentence and one primary button, e.g.
- "Register — it takes 2 minutes";
- "Choose up to 5 employers (2 chosen)";
- "You have 3 talks on 19 March — show my pass";
- "2 employers answered you".

**8.3 Choose one card at a time (both sides).**
- One full card is shown with two big buttons, **Skip** and **I want to meet** (talent) or **Invite** (employer). Arrow keys also work (← skip, → choose). Above the card: "3 of 12" and "Chosen 2 of 5" / "Invites 3 of 8".
- Skipped cards are kept only in the browser (localStorage per event and user). They come back under "Look again at skipped".
- A "Show as a list" toggle keeps the full list for accessibility and power users.
- **Match moment:** when a choice makes the interest mutual, a dialog says "It's a match! <Company> also wants to meet you. Your talk: Thu 19 Mar 14:40, booth A1" (employer side: "It's a match! Person 024 also chose you. Talk at 15:30"). The choose endpoints return the booked meeting when one is created.

**8.4 Secondary material moves down.** Programme, the employer tiles and the floor plan go into a collapsed "About this event" section at the bottom of every step. For anonymous visitors the employer tiles stay open. Meet = pass + meetings + floor plan. Answers = answers, seen-at-the-event, badges, people met, earlier events.

**8.5 Demo bar.** When `/api/config` returns `demo: true` (env `DEMO_MODE`, default on), a thin bar at the very top says "Demo — see as: Jobseeker (Aino) · Employer (Sanna) · Organizer (Leena) · Signed out". One click signs in with the demo account and opens E1 in that role. Seed data must make the match moment demoable:
- at least one E1 employer has already invited Aino and Aino has not chosen it yet;
- at least one E1 person has already chosen Sanna's company and has not been invited yet.
