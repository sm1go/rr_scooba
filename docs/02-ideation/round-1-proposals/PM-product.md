# Round 1 Proposal — PM (Head of Product)

## 1. Problem analysis from my perspective

**The scarce resource is recruiter minutes, not candidates.** TalentMatch events gather 200–1,000 jobseekers and 5–50 employers ([City of Espoo](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events)): 4–200 professionals per company. In 2025 the 1:1 block ran 14:30–17:30 ([City of Espoo](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events/espoo-talentmatch-recruitment-event-2025-information-professionals)); at the standard 15-minute meeting plus 5-minute buffer ([Brella](https://www.brella.io/company-information)) that is nine slots per table. *Assumption:* 20 tables ≈ 180 slots for the "over 300" professionals promised to employers ([City of Espoo](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events/espoo-talentmatch-recruitment-event-2025-information-employers)). Demand also concentrates: in one 43-employer virtual fair, nine employers were fully booked while only ~51% of all slots were taken ([Career Fair Plus](https://blog.careerfairplus.com/virtual-career-fairs-by-the-numbers-a-case-study)). Treating a congested two-sided market like an open directory produces P4 and P7.

**P5 and P6 are one problem seen from two sides.** AI use among active Finnish jobseekers doubled in a year (18% → 37%); the top use (61%) is describing one's own competence ([Duunitori, 2025](https://duunitori.fi/tyoelama/tekoalyn-kaytto-tyonhaussa-tutkimus)). People reach for AI because articulating value is hard (P5), producing look-alike prose that employers filter with AI (P6). In the US, 41% of jobseekers admit to prompt-injection tricks and 34% of recruiters spend up to half their week filtering junk ([Greenhouse, 2025](https://www.greenhouse.com/newsroom/an-ai-trust-crisis-70-of-hiring-managers-trust-ai-to-make-faster-and-better-hiring-decisions-only-8-of-job-seekers-call-it-fair)). Policing text backfires: AI detectors flagged over half of non-native English essays as AI-written ([Liang et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/)), a P10 harm. We must change *what is asked for*: evidence, scarce intent, live structured conversation. Meanwhile, 39% of US hiring managers run more in-person interviews to verify authenticity ([HR Dive, 2025](https://www.hrdive.com/news/the-ai-race-has-fostered-better-hiring-decisions-and-mistrust/805994/)): events can become the place where humans check synthetic signals.

**P1 is downstream of P2–P3.** The pool exists: Espoo–Kauniainen had 18,005 unemployed jobseekers in September 2025, 42.6% foreign-language speakers, and long-term unemployment among university graduates rose ~52% in a year ([City of Espoo](https://www.espoo.fi/en/news/2025/11/labour-market-review-employment-area-espoo-and-kauniainen-september-2025)). Companies doubt it because nobody shows them, early and concretely, evidence matching their need, and nobody can until the need is described (P2).

**Existing platforms are built for symmetric networking (P7).** Brella, Swapcard, Tavata and b2match match self-declared tags or 5–10 "offer/seek" options; Tavata's guide says free text "cannot" be matched and recommends photos because they raise response rates ([Tavata](https://tavata.events/en/guides/one-to-one-meetings-at-events)), a P10 risk. Requests are unlimited: Brella advertises ~40% acceptance against a 15–20% "industry average" ([Brella](https://www.brella.io/blog/10-reasons-brella-is-the-best-event-networking-platform)). Onboarding is form-heavy ("too many fields to fill up", [G2](https://www.g2.com/compare/bizzabo-vs-swapcard)). Everything stops at "meeting booked": nothing structures the 15 minutes, although unstructured interviews predict job performance at ρ≈.19 versus .42 for structured ones ([Sackett et al., 2022](https://doi.org/10.1037/apl0000994)), and nothing closes the loop.

**Journey drop-offs:**
- *Company sign-up → need:* needs late, vague or inflated ("native Finnish", "10+ years") (P2, P10).
- *Talent registration:* CV + tags are generic, AI-polished, unverifiable (P5, P6, P3).
- *Matching → agenda:* floods to big brands, silence for most, scheduling ping-pong (P4, P7).
- *Event day:* login spike, unstructured chats, online participants as spectators (P8, P6, P9).
- *Follow-up:* ghosting and no outcome data, while permit holders who lose a job have 3–6 months to find another ([Migri](https://migri.fi/en/-/changes-to-work-based-residence-permits-protection-period-for-unemployment-and-new-notification-obligation-for-employers)) (P1, P9).

**Jobs-to-be-done.** *Company:* "In one afternoon, show me a few credible people for a concrete problem and make the next step, permits included, easy." *Talent:* "Let me prove what I can do to the few employers who need it, and get an honest answer." *Organiser:* "Get needs early, keep it fair, run a crash-free day, prove outcomes."

**Design principles:** need before person; evidence over prose; scarcity over volume; humans decide, algorithms only arrange; every loop closes. The City is also the employment authority, so event data must never feed benefit casework, or participation becomes coerced and signals distorted. Ranking or filtering candidates is AI Act Annex III high-risk, and profiling always is ([Art. 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6)), with obligations from 2 December 2027 ([Council of the EU](https://www.consilium.europa.eu/en/policies/artificial-intelligence-act/timeline-artificial-intelligence/)); we keep AI preparatory and decisions human.

## 2. Opportunity areas ("How might we…")

- HMW turn a company's late, vague need into a testable challenge three weeks out, and make being early pay? (P2, P1, P10)
- HMW help professionals evidence what they can do, in their own words and language, so AI polish stops being the advantage? (P5, P6, P10)
- HMW make interest scarce and therefore credible, so recruiters see a dozen real signals instead of a hundred generic requests? (P4, P6, P7)
- HMW make every 15-minute conversation structured, comparable and fair, without machines recording or scoring people? (P6, P3, P10)
- HMW run an event day that cannot crash and gives online and abroad professionals real meetings, not a livestream? (P8, P7, P9)
- HMW close every loop within 72 hours and turn outcomes into proof that the City is a serious talent pipeline? (P1, P9)

## 3. Feature ideas

### PM-01: Need Interview → Challenge Card
- **One-liner:** A 12-minute guided interview replaces the employer form and turns "we need a senior developer" into a testable Challenge Card: the 90-day problem, three must-have skills, how each will be checked, and a language/degree reality check.
- **Journey stage:** Pre-event
- **Primary users:** Company | Organizer
- **Pain points addressed:** P2, P10, P9, P1
- **How it works:** At sign-up (target T-21) the hiring manager answers seven fixed questions by chat or voice, or a City coordinator asks them on a company visit, mirroring Espoo's candidate-search kick-off ([City of Espoo, 2026](https://www.espoo.fi/en/news/2026/05/how-your-business-doing-invite-us-visit)). They cover the 90-day outcome, three must-haves and how to check each in 15 minutes, which tasks need Finnish and from when, whether a degree is legally required, and whether it is a hire, project or future need. AI drafts the card with ESCO-coded skills and flags inflated requirements ("native Finnish" in an English-speaking team, "10+ years") as neutral prompts. Approval unlocks the Pool Preview (PM-02); cards approved by T-14 get the whole signal week (PM-04).
- **What makes it new:** It interviews for outcomes and verification, and the same artefact then feeds PM-03, PM-04 and PM-06. Fairness shifts left: years of experience predicts performance at only ρ≈.07 ([Sackett et al., 2022](https://www.annualreviews.org/content/table/10.1146/annurev-orgpsych-020924-072127.t1)), yet even Job Market Finland's matching deducts points for language or education mismatches ([Job Market Finland](https://tyomarkkinatori.fi/en/instructions-and-support/personal-customers/instructions-for-the-my-job-path-section/independent-job-search/how-the-matching-works)).
- **AI role & human-in-the-loop:** LLM structures answers, maps ESCO skills and raises prompts; the company accepts, edits or dismisses each (reasons logged); the organiser approves publication. No jobseeker data is processed.
- **Risks & mitigations (privacy, bias, legal):** Hallucinated requirements → diff view; nothing published unapproved. Genuine legal requirements → "required by regulation" option. Confidentiality → EU-hosted model, no training on customer data.
- **48h prototype:** S — synthetic SME "Nordic Grid Oy" answers; the card renders live with ESCO chips, and "Finnish C1: for which tasks?" becomes "English team language; Finnish for customer calls from month 6".
- **Real-world pilot notes:** Companies with an approved card by T-14 (target ≥70%; baseline to measure), median intake ≤15 min, cards revising a flagged requirement, organiser hours per company. Pilot human-run first.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 5/5

### PM-02: Pool Preview — see the evidence before you commit
- **One-liner:** Once a Challenge Card is approved, the company sees an anonymous, aggregated view of the City's opt-in talent pool ("23 professionals show evidence for all three must-haves, 61 for two") and can reserve slots right there.
- **Journey stage:** Pre-event
- **Primary users:** Company | Organizer
- **Pain points addressed:** P1, P2, P3
- **How it works:** Professionals may opt in to a standing TalentMatch pool with their Evidence Cards (PM-03), optionally pre-filled from their Job Market Finland profile, which uses ESCO-based skills and is mandatory for unemployed jobseekers starting their search from 1 September 2026 ([Job Market Finland](https://tyomarkkinatori.fi/en/teemasivut/job-applicant-profile)). Per card, the system counts evidence-backed matches per must-have (deterministic ESCO codes), shows buckets only when n ≥ 5, and adds up to three anonymised excerpts whose owners agreed to be showcased. Organisers paste preview links into outreach; companies commit slots in one click.
- **What makes it new:** It flips the City's pitch from "trust our free event" to "see the evidence first", attacking the belief that the public pool lacks suitable candidates: in August 2025, 6,679 unemployed jobseekers in Espoo–Kauniainen held university degrees ([City of Espoo](https://www.espoo.fi/en/news/2025/10/labour-market-review-employment-area-espoo-and-kauniainen-august-2025)).
- **AI role & human-in-the-loop:** No AI ranking: counts use skill codes professionals confirmed themselves; nobody is ranked or exposed. The company decides whether to commit.
- **Risks & mitigations (privacy, bias, legal):** Re-identification → n ≥ 5, coarse buckets, no free-text search. Over-promising → counts labelled "evidence, not availability". Separate, renewable pool consent; Job Market Finland import always voluntary.
- **48h prototype:** S — approving the Nordic Grid card triggers a live panel over 300 synthetic Evidence Cards and a "Reserve 9 slots" button.
- **Real-world pilot notes:** A/B outreach (preview link vs standard invitation): conversion and days to commitment; companies agreeing "the City pool is relevant for us" before vs after; repeat participation.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 4/5

### PM-03: Evidence Card — AI as interviewer, not ghostwriter
- **One-liner:** Instead of uploading an AI-polished CV, each professional builds a one-screen Evidence Card with an AI coach that only asks questions ("what exactly did you do, with what, and what changed?") and never writes the answer.
- **Journey stage:** Pre-event
- **Primary users:** Company | Talent
- **Pain points addressed:** P5, P6, P3, P10
- **How it works:** The professional picks up to three claims relevant to published cards and writes a short example for each in their own words and language (original kept; machine translation labelled). The coach asks up to three follow-ups per claim (own action, tools, result), flags vague phrases ("responsible for…") and suggests transferable ESCO mappings, e.g. "army logistics officer → supply chain planning", which the person accepts or rejects. Proof links (repository, portfolio, certificate) are optional. Until both sides agree to meet, the card shows no photo, name, age, nationality or school.
- **What makes it new:** It serves the main reason Finns use AI in job search, describing their competence ([Duunitori, 2025](https://duunitori.fi/tyoelama/tekoalyn-kaytto-tyonhaussa-tutkimus)), but outputs specifics only the person can defend live (PM-06), and skips AI-text detectors, which penalise non-native writers.
- **AI role & human-in-the-loop:** LLM asks questions and suggests mappings; the person accepts or edits everything; nothing is scored, ranked or rejected. The coach discloses it is an AI (AI Act Art. 50).
- **Risks & mitigations (privacy, bias, legal):** Homogenised text → the coach never generates answers. Digital-literacy barriers → voice input, plain language and "Evidence clinics" by City career coaches, extending TalentMatch's transferable-skills workshop ([City of Espoo](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events/espoo-talentmatch-recruitment-event-2025-information-professionals)). Privacy → pseudonymous card, deleted after the event unless pooled.
- **48h prototype:** M — a synthetic career-changer turns "I was responsible for network monitoring" into "I wrote Python scripts that cut incident triage from 40 to 10 minutes"; ESCO chips appear (real LLM, cached ESCO subset).
- **Real-world pilot notes:** Completion (target ≥70% of registrants), median time ≤20 min, claims with a concrete result, recruiter-rated usefulness vs CVs (A/B), self-efficacy ("I can explain my value") before/after.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### PM-04: Three Signals — scarcity makes interest credible
- **One-liner:** Every professional gets three signals per event for the Challenge Cards they care about most, and companies must answer every signal: a bot can write a thousand applications, but it cannot make three signals scarce.
- **Journey stage:** Pre-event
- **Primary users:** Company | Talent
- **Pain points addressed:** P4, P6, P7, P10
- **How it works:** In signal week (T-10 to T-5) professionals browse cards with "why suggested" chips (overlap with their own Evidence Card, visible only to them) and a demand meter ("42 signals for 9 slots"), then spend up to three signals, each with a two-line "why this challenge". The recruiter inbox groups signals by card beside the anonymised Evidence Card; each gets "Meet 1:1", "Invite to Circle" or "Not this time" by T-4, or closes politely. Companies also hold a few invitations for people who did not signal them. No paid boosts, ever.
- **What makes it new:** Platforms allow unlimited requests. Limited signals are proven market design for congested matching: in the 2024 US radiology residency cycle, applicants reported interview rates of 59.8% from signalled programmes vs 8.5% from others ([JACR, 2024](https://www.jacr.org/article/S1546-1440%2824%2900701-4/fulltext)); signalling raised interview odds across gender and under-represented groups, and for international graduates in two of three specialties ([Rosenblatt et al., 2023](https://pmc.ncbi.nlm.nih.gov/articles/PMC10686664/)).
- **AI role & human-in-the-loop:** No AI: suggestion chips are simple overlaps. Talent chooses where to signal; companies decide whom to meet.
- **Risks & mitigations (privacy, bias, legal):** Fear of "wasting" a signal → demand meter, coach tips. Brand hoarding → Circles (PM-05), highlighted SME cards. Ignored signals → deadline, organiser nudges. Duplicates → verified email, de-duplication.
- **48h prototype:** S — a professional spends three signals; in the synthetic demo the recruiter answers 14 signals instead of skimming 140 requests.
- **Real-world pilot notes:** Signals answered by deadline (target ≥95%), acceptance vs today's open requests (baseline: current platform export), talent with ≥1 mutual yes, recruiter-rated meeting relevance.
- **Self-assessment:** J1 5/5 · J2 5/5 · J3 5/5

### PM-05: Fair Agenda Builder — 1:1s, Circles and remote seats
- **One-liner:** A transparent scheduler turns mutual yeses into everyone's agenda with a "one-before-four" fairness floor, gives online and abroad professionals real remote seats, and converts over-demanded cards into 30-minute Challenge Circles.
- **Journey stage:** Pre-event | During event
- **Primary users:** Company | Talent | Organizer
- **Pain points addressed:** P4, P7, P9, P10
- **How it works:** At T-3 the builder takes all mutual decisions, recruiter capacity, tables and each company's remote seat (a laptop at the table, run by a volunteer host). Published rules: no double-booking, 15-minute slots with 5-minute buffers, and nobody gets a fourth meeting while someone with a mutual yes has none. Over-demanded cards become Circles: one recruiter and six professionals work through the card's problem with a facilitation sheet. The organiser reviews alerts ("12 people with no meeting"), adjusts and locks; everyone sees a plain-language reason for their agenda.
- **What makes it new:** Scheduling today is one-to-one ping-pong and hybrid often means broadcast: at TalentMatch 2025, people without an in-person seat could follow pitches by livestream ([City of Espoo](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events/espoo-talentmatch-recruitment-event-2025-information-professionals)). Here humans choose once, fairness rules are explicit, and overflow becomes a richer format.
- **AI role & human-in-the-loop:** No AI: a deterministic optimiser that only places meetings both sides already agreed to; the organiser approves and can override.
- **Risks & mitigations (privacy, bias, legal):** Circles feeling second-class or favouring extroverts → framed as problem-solving sessions with written think-time and turn-taking. Remote seats → audio-only and camera-off allowed, EU-hosted video, no recording.
- **48h prototype:** M — on 300 synthetic professionals × 20 companies, toggling the fairness floor shows the change in people with ≥1 conversation; a Circle is auto-created for a 42-signal card.
- **Real-world pilot notes:** Professionals with ≥1 conversation, slot utilisation, no-shows, meeting spread across companies, Circle vs 1:1 satisfaction, remote participants' conversations, organiser scheduling hours.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### PM-06: Challenge Conversations — 15 minutes, 3 questions, 1 thumb
- **One-liner:** Every 1:1 and Circle runs on a script built from the company's own card: the same three job-relevant questions for every candidate, a 1–4 anchored rating tapped on the recruiter's phone, and a closing "show me" moment.
- **Journey stage:** During event
- **Primary users:** Company | Talent
- **Pain points addressed:** P6, P3, P10, P4
- **How it works:** The "how would you check it" answers from PM-01 become three questions with behavioural anchors, drafted by AI and edited by the recruiter. Professionals see the topics 48 hours ahead, which helps those working in a second language. On the day the recruiter's phone shows a timer, questions, rating rows and notes; the last five minutes are open for the person to show an artefact from their Evidence Card. Ratings stay with the company, never pooled across companies or reused by the City.
- **What makes it new:** Event chats are unstructured interviews (ρ≈.19), while structured interviews are the strongest single predictor of job performance (ρ≈.42) ([Sackett et al., 2022](https://doi.org/10.1037/apl0000994)). Bringing that structure into a 15-minute slot is the most direct antidote to synthetic CVs: the evidence is produced live, by the person.
- **AI role & human-in-the-loop:** AI drafts questions from company-side data only; the recruiter approves; humans conduct and rate. No recording, transcription or face/voice analysis: inferring emotions in the workplace is prohibited by AI Act Art. 5(1)(f) ([AI Act Service Desk](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5)).
- **Risks & mitigations (privacy, bias, legal):** Coldness → three questions plus open time. Rater bias → identical questions and anchors. Data load → ratings are the company's own notes, exportable to its ATS, purged from the platform after 30 days.
- **48h prototype:** S — recruiter phone view with timer, questions and tap ratings, then a side-by-side of three synthetic candidates on the same questions.
- **Real-world pilot notes:** Script adoption (% of meetings), recruiter usefulness rating, candidate-perceived fairness, next-step rate vs unscripted control tables; long term, 6-month retention of hires.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### PM-07: Peak-proof Event Pass — the day needs no login
- **One-liner:** Agendas, table numbers, cards and scripts are pre-delivered as an offline-first pass (web app plus PDF/wallet QR), so the event day has no login spike; online participants get one personal link that opens only for their slot.
- **Journey stage:** During event
- **Primary users:** Company | Talent | Organizer
- **Pain points addressed:** P8, P7
- **How it works:** When the agenda locks (T-2), each person gets a signed magic link that caches a read-only agenda, plus a PDF and a wallet pass with a QR code. Check-in is a QR scan on organiser phones that works offline and syncs later; recruiters' meeting cards and scorecards (PM-06) are cached, encrypted, on their devices. Remote slots open just before they start, so servers only serve people whose meetings are beginning. Changes are pushed as versioned updates with an SMS fallback.
- **What makes it new:** Platforms scale up to survive the start-of-event spike (one virtual job fair peaked at 1,634 concurrent users, [6Connex](https://info.6connex.com/case-studies/kariyer-virtual-job-fair)); we pre-compute the day as static files so the spike never forms. Demo moment: we switch off the Wi-Fi and the event keeps running.
- **AI role & human-in-the-loop:** No AI.
- **Risks & mitigations (privacy, bias, legal):** Stale agendas → version stamp and SMS on change. Lost phones → printed agenda at check-in. Data on devices → minimum fields, encrypted cache, auto-expiry 48 hours after the event.
- **48h prototype:** S — open the pass, switch to airplane mode, check in via QR, record a scorecard offline, reconnect and watch it sync.
- **Real-world pilot notes:** Errors/timeouts in the first 30 minutes (target zero), check-ins per minute, offline agenda views, no-show rate, on-the-day support requests.
- **Self-assessment:** J1 3/5 · J2 4/5 · J3 5/5

### PM-08: 72-hour Closure + Next-Step Desk
- **One-liner:** Every conversation is closed within 72 hours with one tap ("next step", "keep in touch" or "not a fit + one job-related reason"), and each "next step" opens a City desk offering the right public support, permits included.
- **Journey stage:** Post-event
- **Primary users:** Company | Talent | Organizer
- **Pain points addressed:** P1, P9, P5, P10
- **How it works:** Companies accept a response promise at registration: free, but not cheap. Recruiters get a pre-filled list; "not a fit" needs one reason generated from the card's must-haves ("needs hands-on Kubernetes"), sent with a pointer to a relevant City service. "Next step" opens the desk: recruitment services and financial support ([Espoo Talent Hub](https://www.espoo.fi/en/working-life/espoo-talent-hub)), Talent Boost and International House advice ([City of Espoo](https://www.espoo.fi/en/business-espoo-helping-companies-thrive/international-recruitment-assistance)) and, only if the professional chooses to share a permit need, a permit checklist, e.g. fast track for first permits from abroad: decision in about two weeks, employer adds employment terms within two working days ([Migri](https://migri.fi/en/fast-track)). A City specialist calls back within two working days; at +30/+90 days both sides confirm whether a hire or project followed.
- **What makes it new:** Platforms stop at "meeting booked"; today's feedback relies on forms and prize draws ([Espoo Talent Hub on LinkedIn](https://www.linkedin.com/posts/espootalenthub_espoo-talentmatch-2025-tips-part-2-activity-7310284362694975489-TGch)). Closure becomes part of the product contract, producing outcome data that proves the City's value, and the public toolbox appears exactly when hiring intent peaks.
- **AI role & human-in-the-loop:** Optional AI turns the chosen reason into a polite message; the recruiter edits and sends. Outcomes are human statements.
- **Risks & mitigations (privacy, bias, legal):** Discrimination exposure → curated, job-related reason codes only; no free-text judgements of personality or accent. Non-compliance → closure rates visible to the organiser, "reliable responder" badge. Outcomes pseudonymised, reported in aggregate.
- **48h prototype:** S — a recruiter closes six conversations in 30 seconds; the professional gets a respectful feedback card; "Next step → needs permit" shows the checklist and books a City callback.
- **Real-world pilot notes:** 72-hour closure rate (target ≥90%), professionals never answered (target <5%), next steps per conversation, hires/projects at 90 days per event (north star), desk requests, company repeat rate.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### PM-09: Organizer Control Tower with Second Look
- **One-liner:** One cockpit, aggregated by default, showing missing company needs, skill supply/demand gaps, who risks leaving with zero conversations and what each event produced, plus a Second Look queue where City career coaches can sponsor overlooked professionals.
- **Journey stage:** Cross-cutting
- **Primary users:** Company | Talent | Organizer
- **Pain points addressed:** P2, P1, P3, P10
- **How it works:** Pre-event it tracks card completion with one-click nudges and a supply/demand heatmap of ESCO skill clusters ("47 professionals show data-engineering evidence; one card needs it"), prompting targeted company outreach. From T-4 the Second Look queue lists, in random order and only with consent, professionals with no mutual yes; coaches from Espoo's competence centre for highly educated immigrants ([Espoo Talent Hub](https://www.espoo.fi/en/working-life/espoo-talent-hub)) can sponsor up to ten per event with a one-line rationale, shown to the company as a "City coach pick". After the event it reports the funnel signals → meetings → next steps → hires at 90 days, anonymised.
- **What makes it new:** Built around the organiser's real jobs (early needs, balance, fairness, provable outcomes) rather than attendance counts, with an accountable human override for career changers, foreign job titles and non-native writers whom filters and signals miss.
- **AI role & human-in-the-loop:** Optional AI summarises gaps into suggestions; organisers and coaches decide. No individual scoring anywhere.
- **Risks & mitigations (privacy, bias, legal):** Function creep, as the City is also the employment authority → event data firewalled from benefit casework (separate store, purpose limitation, access logs); aggregates with n ≥ 5. Coach favouritism → mandatory rationale, rotation, aggregated audits.
- **48h prototype:** M — heatmap and funnel on synthetic data; a "12 at zero" alert opens the Second Look queue; sponsoring one person updates the company inbox.
- **Real-world pilot notes:** Organiser hours per event, % of needs in by T-14, % of talent with ≥1 conversation, next-step rate of sponsored vs signalled meetings, companies recruited via heatmap gaps.
- **Self-assessment:** J1 4/5 · J2 3/5 · J3 5/5

## 4. My top 3 features (and why)

1. **PM-04 Three Signals** — the most literal implementation of the brief's north star, "stronger signal and less noise". It attacks P4 for companies and P6 for both sides with a mechanism backed by peer-reviewed evidence from another congested market, needs no AI (strong J3) and explains itself in 20 seconds.
2. **PM-03 Evidence Card** — it resolves the challenge's central paradox: people use AI because articulating value is hard (P5), which creates synthetic signal (P6). An AI that interviews instead of ghostwriting turns the same technology into a source of authenticity, the product's main talent-side value.
3. **PM-01 Need Interview → Challenge Card** — everything downstream depends on a concrete, early need. It fixes P2 for companies and organisers, moves fairness upstream (P10) and, with PM-02, gives companies a reason to commit early (P1).

My fourth, as a P1 anchor: **PM-08**, because closure data is how the City proves it is a serious pipeline.

## 5. Hero concept

**TalentMatch Signal — fewer, truer conversations.** One artefact, the Challenge Card, flows through the whole journey and keeps both sides honest. Three weeks out, Nordic Grid Oy (a synthetic SME) completes a 12-minute need interview (PM-01): "native Finnish" becomes "Finnish for customer calls from month 6", and the card goes live. Sam, a synthetic telecom engineer moving into cloud operations, builds an Evidence Card with a coach that only asks questions (PM-03): "I was responsible for monitoring" becomes a specific, defensible story with ESCO skills. In signal week Sam spends one of three signals on Nordic Grid's card (PM-04); the recruiter answers 14 signals instead of skimming 140 requests. On event day the 15-minute slot runs on three questions from Nordic Grid's own card, rated with a thumb (PM-06): evidence produced live, by a person, in front of a person. Within 72 hours Sam gets a real answer; Nordic Grid taps "next step: needs permit" and the City desk returns a permit checklist and a specialist callback (PM-08). The demo is five screens (Need → Proof → Signal → Conversation → Closure) on synthetic data. Judges see AI that interviews rather than ghostwrites, scarcity a bot cannot fake, and humans deciding at every step; Espoo gets early needs, outcome data to win companies, and a pilot path inside its existing TalentMatch series.

## 6. Sources

- [City of Espoo: TalentMatch events](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events)
- [City of Espoo: TalentMatch 2025, professionals](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events/espoo-talentmatch-recruitment-event-2025-information-professionals)
- [City of Espoo: TalentMatch 2025, employers](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events/espoo-talentmatch-recruitment-event-2025-information-employers)
- [City of Espoo: Espoo Talent Hub](https://www.espoo.fi/en/working-life/espoo-talent-hub)
- [Espoo Talent Hub: feedback contest post (LinkedIn)](https://www.linkedin.com/posts/espootalenthub_espoo-talentmatch-2025-tips-part-2-activity-7310284362694975489-TGch)
- [City of Espoo: company visits, May 2026](https://www.espoo.fi/en/news/2026/05/how-your-business-doing-invite-us-visit)
- [City of Espoo: international recruitment assistance](https://www.espoo.fi/en/business-espoo-helping-companies-thrive/international-recruitment-assistance)
- [City of Espoo: labour market review, September 2025](https://www.espoo.fi/en/news/2025/11/labour-market-review-employment-area-espoo-and-kauniainen-september-2025)
- [City of Espoo: labour market review, August 2025](https://www.espoo.fi/en/news/2025/10/labour-market-review-employment-area-espoo-and-kauniainen-august-2025)
- [Duunitori: AI in job search 2025 (Finnish)](https://duunitori.fi/tyoelama/tekoalyn-kaytto-tyonhaussa-tutkimus)
- [Greenhouse: 2025 AI in Hiring Report](https://www.greenhouse.com/newsroom/an-ai-trust-crisis-70-of-hiring-managers-trust-ai-to-make-faster-and-better-hiring-decisions-only-8-of-job-seekers-call-it-fair)
- [HR Dive: Greenhouse report, November 2025](https://www.hrdive.com/news/the-ai-race-has-fostered-better-hiring-decisions-and-mistrust/805994/)
- [Liang et al. (2023): GPT detectors and non-native writers](https://pmc.ncbi.nlm.nih.gov/articles/PMC10382961/)
- [Sackett et al. (2022): selection validity revisited](https://doi.org/10.1037/apl0000994)
- [Annual Reviews: validity estimates table](https://www.annualreviews.org/content/table/10.1146/annurev-orgpsych-020924-072127.t1)
- [Brella: company information](https://www.brella.io/company-information)
- [Brella: acceptance-rate claims](https://www.brella.io/blog/10-reasons-brella-is-the-best-event-networking-platform)
- [Tavata: running 1:1 meetings at events](https://tavata.events/en/guides/one-to-one-meetings-at-events)
- [G2: Swapcard reviews](https://www.g2.com/compare/bizzabo-vs-swapcard)
- [Career Fair Plus: virtual fair case study](https://blog.careerfairplus.com/virtual-career-fairs-by-the-numbers-a-case-study)
- [6Connex: Kariyer.net virtual job fair](https://info.6connex.com/case-studies/kariyer-virtual-job-fair)
- [JACR (2024): radiology preference signaling](https://www.jacr.org/article/S1546-1440%2824%2900701-4/fulltext)
- [Rosenblatt et al. (2023): preference signals across specialties](https://pmc.ncbi.nlm.nih.gov/articles/PMC10686664/)
- [Job Market Finland: job applicant profile](https://tyomarkkinatori.fi/en/teemasivut/job-applicant-profile)
- [Job Market Finland: how the matching works](https://tyomarkkinatori.fi/en/instructions-and-support/personal-customers/instructions-for-the-my-job-path-section/independent-job-search/how-the-matching-works)
- [Migri: fast track](https://migri.fi/en/fast-track)
- [Migri: work-based permit changes, June 2025](https://migri.fi/en/-/changes-to-work-based-residence-permits-protection-period-for-unemployment-and-new-notification-obligation-for-employers)
- [AI Act Service Desk: Article 5](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5)
- [AI Act Service Desk: Article 6](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-6)
- [Council of the EU: AI Act timeline](https://www.consilium.europa.eu/en/policies/artificial-intelligence-act/timeline-artificial-intelligence/)
