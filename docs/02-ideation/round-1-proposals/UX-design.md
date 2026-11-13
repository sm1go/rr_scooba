# Round 1 Proposal — UX (Head of Design & User Research)

## 1. Problem analysis from my perspective

**Thesis: synthetic signal is an interface-genre problem before it is an AI problem.** Hand people a blank box ("describe yourself", "why are you the right fit?") and the rational 2026 move is to let an LLM fill it: about 4 in 10 candidates already use AI in applications ([Gartner via HR Dive](https://www.hrdive.com/news/fake-job-candidates-ai/757126/)); LinkedIn handles ~11,000 applications a minute, up 45% in a year ([Ars Technica/NYT](https://arstechnica.com/ai/2025/06/the-resume-is-dying-and-ai-is-holding-the-smoking-gun/)). Detection is no exit: AI-text detectors flagged on average 61% of non-native English essays as AI-written ([Stanford HAI](https://hai.stanford.edu/news/ai-detectors-biased-against-non-native-english-writers)), punishing exactly the international talent Espoo wants (P10). So we change the genres: **from writing to telling, pointing, showing and meeting.**

- **Today's format manufactures noise.** TalentMatch gathers 200–1,000 jobseekers and 5–50 employers per event, in English; talents are told to "reach out to recruiters with a clear message about why you're the right fit" because 1:1 slots are limited ([Espoo](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events), [Work in Finland](https://www.workinfinland.com/en/open-jobs/talent-match-espoo-2024/)). Recruiters get polished sameness (P4, P6); talents get silence.
- **The perceived audience shapes the signal:** across 12 studies (N = 13,342), people presented themselves as more analytical when they believed AI assessed them ([PNAS 2025](https://www.pnas.org/doi/abs/10.1073/pnas.2425439122)).
- **Structure beats chat:** structured interviews predict job performance at .42, unstructured ones at .19, years of experience at .07 ([Sackett et al. 2022](https://doi.org/10.1037/apl0000994)).
- **Bias is measured locally:** in 2024, Somali-named applicants with identical Finnish qualifications needed 2.48× as many applications as Finnish-named ones to get a callback ([TEM via Helsinki Times](https://www.helsinkitimes.fi/themes/themes/education/176-information/study/26032-foreign-names-still-face-barriers-in-finnish-job-market-study-shows.html)); 41% of international experts in an engineering-union survey report prejudice or discrimination in job search ([IL/TEK 2024](https://www.helins.fi/wp-content/uploads/2024/08/International-experts-2024-results.pdf)).
- **Inclusion is mainstream:** 25.9% of Espoo residents are foreign-language speakers ([Espoo](https://www.espoo.fi/en/city-and-decision-making/research-and-statistics/population)); 11–14% of people in Finland need easy-to-read language ([Selkokeskus](https://selkokeskus.fi/selkokieli/selkokielen-tarve/)).
- **In-person is a trust asset:** 62% of candidates are more likely to apply when in-person interviews are required (Gartner via HR Dive).

**Moments that matter:** *the blank box* (where synthetic text is born), *the silence* (unanswered requests), *the wall of sameness* (identical pitches), *doorway overwhelm* (crowds, a platform loading at opening, the loudest winning), *keyword reduction* ("no Finnish") and *the black hole* (no follow-up, feeding "free means low quality", P1). Existing tools optimise profiles, keywords and filtering; nobody designs the room, the conversation and the ending.

**Synthetic personas (C2):**
- **Amira, 34 — international spouse, backend engineer (S2).** *Goal:* a role at her level. *Frustration:* 150 applications, silence; an AI-polished CV like everyone's. *Great event:* "Three conversations with people who can judge my work, and an answer afterwards."
- **Jukka, 52 — Finnish career changer (S2).** Ex-logistics supervisor, new data-analytics course, phone-first. *Goal:* be seen beyond his age and old title. *Frustration:* platforms want keywords he lacks. *Great event:* "Someone asks how I solved real problems."
- **Linh, 24 — new Aalto graduate (S2).** Introverted, on a post-study job-search permit. *Goal:* a first job before the permit ends. *Frustration:* 40 booths, no plan. *Great event:* "A plan for my afternoon, and nobody judging my accent."
- **Sanna, 41 — SME founder (S1).** 14 staff, no HR. *Goal:* her first DevOps hire. *Frustration:* a job ad costs her a weekend; she doubts a free City event. *Great event:* "Five relevant conversations in two hours."
- **Mikael, 38 — corporate talent-acquisition partner (S1).** Swedish/Finnish bilingual. *Goal:* a qualified, diverse pipeline. *Frustration:* hiring managers skip events; leads die in spreadsheets. *Great event:* "Leads my hiring managers want, with notes they trust."
- **Leena, 45 — City event coordinator (S3).** *Goal:* prove impact. *Frustration:* needs arrive two days before; the platform buckles at opening. *Great event:* "Companies come back, with their hiring managers."

## 2. Opportunity areas ("How might we…")

1. HMW replace the blank box, where synthetic CVs are born, with formats that draw out real stories in each person's strongest language? (P5, P6, P10)
2. HMW capture the hiring manager's real problem in three minutes, weeks before the event, because doing it early pays off at once? (P2, P1)
3. HMW make every meeting request a scarce, evidence-backed signal instead of a persuasive essay? (P4, P6, P10)
4. HMW make capability witnessed live, with an equal turn for introverts, second-language speakers and remote participants? (P3, P6, P9, P10)
5. HMW make the event day impossible to crash and navigable without an app or login? (P7, P8)
6. HMW close every loop, so talent never leaves in silence and the City can prove its quality? (P1, P4)

## 3. Feature ideas

### UX-01: Story Interview — "Tell it, don't type it"
- **One-liner:** A 10-minute voice-or-chat interview in the talent's strongest language that turns three concrete work episodes into editable Story Cards: no CV, no blank box.
- **Journey stage:** Pre-event
- **Primary users:** Talent, Organizer
- **Pain points addressed:** P5, P6, P3, P7, P10
- **How it works:** Passwordless sign-up (WCAG 2.2 Accessible Authentication), then a choice of language (FI, SV, EN, easy-to-read Finnish, Russian, Arabic…) and channel: speak, type, or sit with a City counsellor at a library "Story Booth". A labelled AI interviewer asks episodic prompts ("Tell me about something that broke and how you fixed it"), probing for tools, numbers and constraints, never age, origin or family. It drafts three cards: headline, a three-line story with the person's own words as marked quotes, suggested ESCO skills, and "evidence I can show". Nothing is shared until the talent approves.
- **What makes it new:** A behavioural interview at intake replaces the genre that breeds synthetic text: specific episodes are hard to fabricate and easy to probe live, whether Linh types English or Jukka speaks Finnish into his phone.
- **AI role & human-in-the-loop:** Transcription, follow-up questions, drafting and skill suggestions; the talent authors and approves. No scoring, ranking or personality inference, and no voice-emotion analysis, which the AI Act bans for candidates (Art. 5(1)(f), per Commission guidelines).
- **Risks & mitigations (privacy, bias, legal):** Audio deleted after transcription; volunteered special-category data removed; AI disclosure (Art. 50). Marked verbatim quotes stop AI polishing the person away; no dates on cards, limiting age inference.
- **48h prototype:** M — voice-enabled web chat, five scripted prompts, LLM drafting, edit/approve UI, local ESCO subset; demo: Jukka speaks 60 seconds of Finnish and gets three bilingual cards.
- **Real-world pilot notes:** Co-run with Employment Services counsellors before one TalentMatch, plus a two-week library booth; measure completion, time to first card and "sounds like me" agreement.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### UX-02: Problem Cards with live Pool Preview — "Bring a problem, not a profile"
- **One-liner:** A hiring manager's 3-minute voice memo becomes a one-screen Problem Card that HR approves, and the company instantly sees consented, anonymised stories from the City's pool that fit it.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P2, P1, P3, P4
- **How it works:** Via a no-account link, the hiring manager answers four prompts: "What is broken that this person fixes in the first 90 days?", "What is needed on day one vs. learnable here?", "Who will they work with, in which language?" (feeds UX-03), "What would impress you in 10 minutes?". AI drafts the card and three questions for every 1:1 (UX-07), flagging vague or exclusionary wording ("rockstar", "native Finnish"); HR edits and approves. Meanwhile a Pool Preview shows thresholded counts ("17 registrants describe CI/CD work"; exact only when ≥5) and three opted-in, anonymised Story Cards. Cards approved ≥14 days ahead get first access to scheduling.
- **What makes it new:** Companies describe problems far better than people, and the first-90-days problem is concrete, owned by whoever knows it and reusable in conversations. Seeing real people who fit is an instant payoff that fixes timing and answers the "no suitable candidates" doubt (P1).
- **AI role & human-in-the-loop:** AI structures, flags and maps card lines to skills for aggregate counts only; hiring manager and HR approve; City staff curate featured stories. No individual is assessed.
- **Risks & mitigations (privacy, bias, legal):** Confidential lines can stay "internal"; transcript shown beside the card against hallucinations; audio deleted. Pool stories: per-card opt-in, talent-approved anonymisation (no names, employers, dates), revocable; counts labelled "self-described, not verified".
- **48h prototype:** S — voice/text form → LLM → Problem Card with flags, questions and preview panel on synthetic data; demo with Sanna's SME.
- **Real-world pilot notes:** Plug into TalentMatch employer registration. KPIs: days before the event when needs are final (baseline: "just before the event day"), hiring-manager authorship, registration conversion.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### UX-03: Language Reality Layer
- **One-liner:** Replace "Finnish required" with situational can-do language needs on both sides; everyone writes in their strongest language and readers see a labelled translation, original one tap away.
- **Journey stage:** Cross-cutting
- **Primary users:** Talent, Company, Organizer
- **Pain points addressed:** P9, P10, P5
- **How it works:** Companies rate six situations in the Problem Card (e.g., team meetings, customer calls, safety instructions, authority paperwork) as not needed / helpful / essential, "from day one" or "within 12 months", and tick "we support learning". Talents describe working languages against the same situations as "I can…" statements; mother tongue is never asked. The UI shows a readable fit, not a hidden filter: "fits 5 of 6 situations; Finnish customer calls expected within 12 months; company pays a course". Cards are translated for readers with an "AI-translated · show original" label. Badges show language names, never flags.
- **What makes it new:** A blunt gatekeeping proxy becomes an explicit, discussable requirement with one vocabulary for both sides. "Show original" stops translation silently rewriting someone's voice; Espoo's own HelloEspoo experiment found AI translation suits clear, simple content and needs trust-building guidance.
- **AI role & human-in-the-loop:** Translation for display only, never to judge proficiency. Companies set requirements, a City advisor may challenge "essential from day one", and hard requirements are shown and logged, never silently applied.
- **Risks & mitigations (privacy, bias, legal):** Translation errors → original always visible, short plain-language cards. Self-reported ability → labelled "self-described". No mother-tongue or nationality fields (ethnicity proxies).
- **48h prototype:** S — situation grid on both sides, fit summary, translation toggle.
- **Real-world pilot notes:** Test at one English- and one Finnish-language event; track how often "essential from day one" gets softened (assumption: often).
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### UX-04: Sparks — "Point, don't write" meeting requests
- **One-liner:** Meeting requests become five scarce "Sparks": pair one of your Story Cards with one line of a company's Problem Card instead of writing a pitch; companies review evidence pairs skills-first, names later.
- **Journey stage:** Pre-event, During event
- **Primary users:** Talent, Company
- **Pain points addressed:** P4, P6, P10, P5
- **How it works:** Each talent gets five Sparks per event; companies get Invites. Amira taps the line "our CI pipeline takes 40 minutes" on Sanna's card, then her Story Card "cut build time from 30 to 6 minutes" (no dragging needed: WCAG 2.2 Dragging Movements), plus an optional 140-character note. Sanna's inbox shows "problem ↔ evidence" pairs grouped by her own problem lines, not by an AI score, with name, photo and nationality hidden until she accepts. Declined Sparks, or ones unanswered after 72 h, return marked "closed", so silence never costs a Spark.
- **What makes it new:** It deletes the persuasion-writing task where AI slop is mass-produced and non-native writers are penalised, replacing it with evidence-linking: quick for a human, pointless for a bot. Scarcity makes each request an honest signal; staged reveal adds blind-review fairness to pre-booking.
- **AI role & human-in-the-loop:** Optional, explained "stories that fit this line" suggestions for talents; no candidate ranking for companies. Companies decide whom to meet; talents decide where to spend Sparks.
- **Risks & mitigations (privacy, bias, legal):** Poor choices → refunds and human-granted extra Sparks (UX-09). Staged reveal covers pre-booking only (faces are visible on the day). Decision logs feed aggregate fairness reviews. Suggestions likely fall under AI Act Annex III (employment): oversight is built in before high-risk rules apply (2 Dec 2027).
- **48h prototype:** M — Spark composer and company inbox of evidence pairs with reveal-on-accept, seeded with 30 synthetic talents and 5 companies.
- **Real-world pilot notes:** A/B at an online TalentMatch: message requests vs. Sparks. KPIs: recruiter minutes per request, acceptance rate, share of talents with ≥1 meeting.
- **Self-assessment:** J1 5/5 · J2 5/5 · J3 4/5

### UX-05: Signal Ladder — provenance chips instead of AI detectors
- **One-liner:** Every piece of information carries a chip saying how it came to be ("own words", "AI-drafted · approved by author", "witnessed live", "introduced by a person"), so recruiters weigh genuine human signal without guessing who used AI.
- **Journey stage:** Cross-cutting
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P6, P3, P10
- **How it works:** The system records how content was produced, not what it "looks like": verbatim quotes from UX-01 get "own words", AI-structured text "AI-drafted · approved by Amira", a table host's note (UX-07) "witnessed live", a Connector intro (UX-09) "introduced by Leena, City of Espoo", links "evidence attached · not verified". Chips form a visible ladder from easiest to hardest to fake, explained in one tap; talents get nudges such as "Join a Challenge Table to add a witnessed signal".
- **What makes it new:** It answers P6 with process transparency instead of an AI-versus-AI arms race. Detectors misjudge non-native writers; provenance chips are fair by construction and teach everyone what trustworthy signal looks like.
- **AI role & human-in-the-loop:** No AI judgement: chips are deterministic metadata from human actions, and humans weigh them.
- **Risks & mitigations (privacy, bias, legal):** "Witnessed" could favour in-person attendees → online tables and window seats offer the same rung. Chips never become a score or a filter that hides people. Witness notes are visible to the person described (GDPR access by design).
- **48h prototype:** S — chip and tooltip component used across all demo screens.
- **Real-world pilot notes:** Recruiter usability test: do chips change which approaches get opened first, and are they understood without training?
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### UX-06: "Ask me about" badges & Story Cards — the No-CV event
- **One-liner:** CVs go to the coat check: talents wear a badge with a real story hook and carry three printed Story Cards, companies wear their problem, and QR codes open only what each person chose to share.
- **Journey stage:** During event
- **Primary users:** Talent, Company
- **Pain points addressed:** P5, P6, P4, P10
- **How it works:** Talent badges read "Ask me about: how I automated shift planning for 120 warehouse workers" plus working languages; company badges read "Ask us about: our 40-minute CI pipeline · hiring manager here 13–15". Talents collect three printed Story Cards at check-in. A QR scan shows that card and a "Connect" button; contacts are exchanged only on mutual consent. No phone? The recruiter writes on the paper card and drops it in the company box for staff to digitise. Lanyard clips signal "open to chat / in a meeting / on a break".
- **What makes it new:** A physical, playful artefact that carries genuine signal (stories, not titles), gives introverts and second-language speakers a ready opening line, and works with zero app adoption.
- **AI role & human-in-the-loop:** No AI on the day; content is the talent-approved output of UX-01.
- **Risks & mitigations (privacy, bias, legal):** Badges are public → talents choose the hook; first name optional; no photo. QR links expire 30 days after the event; no scan tracking beyond mutual connects. Large-print, high-contrast versions.
- **48h prototype:** S — badge and card PDF generator plus mutual-connect QR; printed cards as pitch props.
- **Real-world pilot notes:** One in-person TalentMatch (~300 talents); exit survey on conversations started from a hook and their relevance for recruiters.
- **Self-assessment:** J1 4/5 · J2 5/5 · J3 5/5

### UX-07: Challenge Tables & Table Tents — problem-first, structured conversations
- **One-liner:** Booths give way to 20-minute round tables where rotating groups tackle a company's Problem Card, and 12-minute 1:1s run on a printed "table tent" with the same questions for every candidate.
- **Journey stage:** During event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P6, P3, P4, P10, P9
- **How it works:** Talents book up to three rounds: six seats plus a "window seat" for a remote participant on a captioned tablet. Each round: 3 minutes of framing by the hiring manager, 2 of silent writing (so the fluent and loud don't dominate), 12 of round-robin discussion, 3 of wrap-up. The host taps per person "1:1 today / interview later / thanks", plus an optional job-related witness note the participant can read. Afternoon 1:1s run at numbered pods with a folded tent (problem line, the talent's Story Card, three approved questions plus one from the talent) and a 4/6/2-minute timer; both tap the outcome before standing up.
- **What makes it new:** Capability shows in live problem-solving, a low-stakes work sample instead of booth small talk, and a host meets 18 people an hour meaningfully. Tents bring structured-interview discipline (the most predictive method in Sackett et al., 2022) into a job-fair chat, on crash-proof paper.
- **AI role & human-in-the-loop:** No AI at tables or pods, no recording; AI only drafts plain-language briefs and questions for the hiring manager to approve. Invitations and outcomes are human decisions.
- **Risks & mitigations (privacy, bias, legal):** Group dynamics → write-first and round-robin rules on a host card. Not free consulting → framing-level problems only. Notes use a job-related template, are visible to the person described and kept briefly (retention set with the City's DPO). Hearing loop, captions, reserved seats.
- **48h prototype:** M — table booking, host tap-screen with witness notes, tent PDF with timer; demo a round with three synthetic talents, then Sanna × Amira at a pod.
- **Real-world pilot notes:** Run six tables and twenty pods beside classic booths at one TalentMatch; compare invitations per host-hour and talent satisfaction.
- **Self-assessment:** J1 5/5 · J2 5/5 · J3 4/5

### UX-08: Zero-login event day & floor choreography
- **One-liner:** Nobody logs in on the day: every schedule is pre-generated as an offline ticket, SMS and printable card, while staggered arrival waves, a virtual booth queue and colour-coded zones replace the opening-time stampede.
- **Journey stage:** During event, Cross-cutting
- **Primary users:** Talent, Company, Organizer
- **Pain points addressed:** P8, P7, P4, P10
- **How it works:** 24 h before, schedules freeze and everyone gets a cached ticket (offline web page, SMS/email, PDF): arrival wave (12:40, 13:00 or 13:20), tables, pods, map. Staff scan QR check-ins offline. Busy booths show a "Queue me" QR: pick the problem you came for, get a text five minutes before your turn, keep exploring. Zones match ticket colours (Pitch Stage, Challenge Tables, quiet 1:1 Pods, Open Floor, Quiet Room, Connector Desk), with one help point always in the same place, a physical twin of WCAG 2.2 Consistent Help. Changes go out as short text deltas, not app reloads.
- **What makes it new:** It designs the peak away (static, pre-computed, offline) instead of scaling servers, and treats the event as a physical choreography with software backstage. The queue is a fairness device for introverts and people with mobility needs.
- **AI role & human-in-the-loop:** No AI; deterministic scheduling; staff handle exceptions.
- **Risks & mitigations (privacy, bias, legal):** Phone numbers optional (email/print fallback); the ticket holds only first name, times and places. Screen-reader-friendly ticket; large-print agenda at check-in.
- **48h prototype:** S — static ticket generator with an offline service worker, simulated queue texts, SVG floor map.
- **Real-world pilot notes:** At the next in-person event, measure check-in minutes, peak requests at opening, queue waits and no-shows.
- **Self-assessment:** J1 4/5 · J2 3/5 · J3 5/5

### UX-09: Connector Desk — human matchmakers with an AI clipboard
- **One-liner:** City staff act as visible "Connectors" with a console that suggests explainable warm introductions and shows who still has zero meetings; the human decides and introduces in person, so nobody leaves empty-handed.
- **Journey stage:** Pre-event, During event
- **Primary users:** Organizer, Talent, Company
- **Pain points addressed:** P1, P3, P4, P10
- **How it works:** 48 h before, the console lists talents with zero confirmed meetings and companies with free slots, plus unranked pairing ideas explained by shared problem/evidence lines. Connectors offer such talents an extra Spark, a table seat, a 7-minute "reality check" with a hiring manager, or a counsellor. On the day, Connectors in vests staff a desk and roam; a recruiter can ask "anyone who has done X?" and be walked over to a person. Every intro is logged with the Connector's name (the "introduced by" rung of UX-05); Leena's board shows live aggregate supply and demand.
- **What makes it new:** It productises the City's unique asset, staff who know the pool, as a concierge service that answers "free = low quality" (P1). AI is a clipboard, not a judge.
- **AI role & human-in-the-loop:** AI proposes unranked, explained pairings; Connectors decide; both parties consent to any intro (designed for GDPR Art. 22 and AI Act human oversight).
- **Risks & mitigations (privacy, bias, legal):** Connector bias → structured reasons, logged intros, aggregate fairness review after each event. Role-based access; no sensitive data. Staffing cost → focus on zero-meeting cases.
- **48h prototype:** M — console with zero-meeting list, explained suggestions and intro logging; demo: Leena spots Jukka and introduces him to a logistics-software SME.
- **Real-world pilot notes:** 3–4 Connectors per ~300 talents (assumption). KPIs: share of talents with ≥1 meaningful conversation; company satisfaction with intros.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### UX-10: Closure Loop — no ghosting, fading data
- **One-liner:** Every connection gets an answer within 72 hours (two taps for the company plus an AI-drafted, human-approved message), and its data visibly fades after 30 days unless both sides keep it.
- **Journey stage:** Post-event
- **Primary users:** Talent, Company, Organizer
- **Pain points addressed:** P1, P5, P10
- **How it works:** The company dashboard counts "loops to close" across Sparks, table invites and 1:1s. Each needs an outcome (interview / keep in touch / not this time) and a reason chip from a vetted, job-related library ("role filled", "Finnish customer calls from day one, as stated in our card"). AI drafts a specific, kind message; the recruiter edits and sends, and the talent also gets one next step linked to a City service. Open loops trigger reminders; each company's event report shows its closure rate against the event average. Each connection shows a fading-ink timer ("dissolves in 30 days · keep?") and is deleted unless both tap keep.
- **What makes it new:** It designs the ending, where trust in the City's service is won or lost, and turns closure into a measurable service standard the City can show companies (P1). "Fading ink" makes data minimisation tangible.
- **AI role & human-in-the-loop:** AI drafts; humans choose outcomes and send. No automated rejections.
- **Risks & mitigations (privacy, bias, legal):** Reason library reviewed by RAI/legal to stay job-related; a language reason is offered only if it matches the company's own grid (UX-03). Deletion by default supports storage limitation.
- **48h prototype:** S — closure screen with chips, LLM draft and edit, talent inbox, fading timer.
- **Real-world pilot notes:** KPIs: closure rate within 72 h (target, assumption: ≥80%), talent satisfaction, company return rate at the next event.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

## 4. My top 3 features (and why)

1. **UX-04 Sparks — "Point, don't write".** The sharpest answer to the brief's central tension (P4 + P6): it removes the task AI mass-produces and replaces it with evidence-linking only a human does meaningfully. Fewer, better approaches for recruiters; an honest, refundable, skills-first shot for talents. Cheap to build, memorable to demo.
2. **UX-02 Problem Cards with Pool Preview.** P2 is the brief's most concrete operational pain; the card is the backbone every other feature reuses, and the preview rewards early briefs while answering P1 with real people.
3. **UX-07 Challenge Tables & Table Tents.** Capability witnessed live, the signal no AI can fake, in a format that sets City events apart from any job board.

UX-01 is the indispensable talent-side twin of UX-02; build them together.

## 5. Hero concept

**Common Table**: *"Companies bring a problem. Talent brings a story. Espoo sets the table."* The job ad and the CV are replaced by two human-authored objects, the Problem Card (UX-02) and Story Cards (UX-01); everything else connects them.

Demo (three minutes, two phones, one printed tent): Sanna records her memo three weeks early ("our CI pipeline takes 40 minutes"), and the Pool Preview instantly shows 17 people with CI/CD experience. Amira approves her card "cut build time from 30 to 6 minutes" and spends one of five Sparks (UX-04) pairing the two, with no essay. Sanna sees the evidence pair, accepts, and only then sees Amira's name. On the day nobody logs in: Amira's offline ticket sends her to Challenge Table 4 (UX-07), where Sanna watches how she thinks and leaves a "witnessed live" note, then to a structured 1:1 at pod 7. Within 72 hours Amira gets an answer and a next step (UX-10), as does everyone who sparked Sanna. The City finally has early needs, real stories, witnessed signal and closure rates that prove its quality to the next company.

## 6. Sources

- [City of Espoo — TalentMatch recruitment events](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events)
- [Work in Finland — TalentMatch x IT online event (Dec 2024)](https://www.workinfinland.com/en/open-jobs/talent-match-espoo-2024/)
- [City of Espoo — Population statistics, end of 2025](https://www.espoo.fi/en/city-and-decision-making/research-and-statistics/population)
- [City of Espoo — AI translation experiment has ended (2026)](https://www.espoo.fi/en/news/2026/09/espoos-ai-translation-experiment-has-ended)
- [HR Dive — Gartner candidate surveys (2025)](https://www.hrdive.com/news/fake-job-candidates-ai/757126/)
- [Ars Technica — "The résumé is dying" (2025)](https://arstechnica.com/ai/2025/06/the-resume-is-dying-and-ai-is-holding-the-smoking-gun/)
- [PNAS — AI assessment changes human behavior (2025)](https://www.pnas.org/doi/abs/10.1073/pnas.2425439122)
- [Stanford HAI — AI detectors biased against non-native English writers (Patterns, 2023)](https://hai.stanford.edu/news/ai-detectors-biased-against-non-native-english-writers)
- [Sackett et al. — Validity in personnel selection, J. Applied Psychology (2022)](https://doi.org/10.1037/apl0000994)
- [Helsinki Times — Foreign names still face barriers in Finnish job market (2025)](https://www.helsinkitimes.fi/themes/themes/education/176-information/study/26032-foreign-names-still-face-barriers-in-finnish-job-market-study-shows.html)
- [TEM — Reception of immigrants into Finnish working life, 2016 vs 2024 (2025)](https://julkaisut.valtioneuvosto.fi/items/ec1819df-98bb-481c-a9fa-3e71d4da3ce2/full)
- [IL & TEK — International experts in Finland survey (2024)](https://www.helins.fi/wp-content/uploads/2024/08/International-experts-2024-results.pdf)
- [Selkokeskus — Need for easy-to-read language (2025)](https://selkokeskus.fi/selkokieli/selkokielen-tarve/)
- [European Commission — Guidelines on prohibited AI practices](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-01/guide-prohibited_en.pdf)
- [Freshfields — Emotion-recognition ban also covers candidates](https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/eu-ai-act-unpacked-25-european-commission-releases-critical-ai-act-implementati-102kfql)
- [Council of the EU — AI Act timeline](https://www.consilium.europa.eu/en/policies/artificial-intelligence-act/timeline-artificial-intelligence/)
- [Traficom — Accessibility requirements of the Act on the Provision of Digital Services](https://www.saavutettavuusvaatimukset.fi/en/requirements-act-provision-digital-services-0)
- [W3C — What's new in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/)
