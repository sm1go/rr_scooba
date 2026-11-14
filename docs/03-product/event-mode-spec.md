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
