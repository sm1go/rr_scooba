# Round 1 Proposal — TAL (Talent Acquisition & International Recruitment Expert)

## 1. Problem analysis from my perspective

Seven insights from both sides of the booth:

**1. A job fair is a mass unstructured interview (P3, P4, P10).** A booth recruiter has a few minutes per person (practitioner observation) and screens CVs in seconds ([Ladders, 2018: 7.4 s](https://www.theladders.com/career-advice/why-do-recruiters-spend-only-7-4-seconds-on-resumes)). What survives that triage are proxies: familiar employer names, fluent Finnish small talk, a familiar-sounding name. Yet structured interviews (validity .42), job-knowledge tests (.40) and work samples (.33) far outpredict unstructured interviews (.19) and years of experience (.07) ([Sackett et al., 2022](https://doi.org/10.1037/apl0000994)). Proxies are where bias lives: in a 2024 field experiment for the employment ministry, equally qualified applicants with Somali, Iraqi, Russian and English names needed 2.5, 2.0, 1.9 and 1.4 times as many applications as Finnish-named ones for the same number of interview invitations ([TEM](https://tem.fi/en/-/study-jobseekers-with-foreign-names-receive-fewer-employment-opportunities)).

**2. Generative AI turned applications into cheap talk (P6).** On Freelancer.com, employers stopped paying a premium for tailored applications once LLMs arrived; the authors' model counterfactual has top-quintile workers hired 19% less often and bottom-quintile workers 14% more often ([Galdin & Silbert, 2025](https://arxiv.org/abs/2511.08785)). Detecting AI is the wrong fix: GPT detectors flag more than half of non-native English essays as AI-written ([Liang et al., 2023](https://doi.org/10.1016/j.patter.2023.100779)), so they would punish exactly Espoo's international talent. The fix is signals that are costly, scarce or live: work done, reasoning explained, interest that cannot be multiplied.

**3. Part of the noise is structural (P4, P1).** Unemployed jobseekers must, as a rule, apply for four jobs a month ([TEM](https://tem.fi/en/-/individual-services-to-support-job-search-in-the-nordic-labour-market-service-model)), and since 1 September 2026 must publish a Job Market Finland profile within 15 working days ([Työmarkkinatori](https://tyomarkkinatori.fi/uutiset/tyonhakuprofiilin-julkaisemisesta-velvoittavaa-poks)). Obligations create volume, not intent; companies experience it as irrelevant approaches and conclude the pool is weak.

**4. The pool is better than its reputation (P1).** In March 2026, 42.3% of unemployed jobseekers in the Espoo–Kauniainen area were foreign-language speakers: 8,136 people, 2,548 of them with tertiary education ([City of Espoo](https://espoo-sv.oncloudos.com/kokous/20261673-3-354122.PDF)). Supply exists; the signal does not travel.

**5. Needs are vague because nobody runs an intake (P2).** SMEs rarely employ recruiters, so ads become wish lists ("M.Sc., 5+ years, fluent Finnish"). Editing ads is not enough: after US firms dropped degree requirements, hiring changed in fewer than 1 in 700 hires ([Burning Glass Institute & HBS, 2024](https://www.burningglassinstitute.org/research/skills-based-hiring-the-long-road-from-pronouncements-to-practice)); the evaluation must change too. Language requirements are inflated and hidden: 60% of Finnish employers see language as a major obstacle to hiring foreign workers ([OECD, 2025](https://www.oecd.org/en/publications/oecd-economic-surveys-finland-2025_985d0555-en/full-report/enriching-human-capital-with-more-foreign-talent_5745d827.html)), and international experts cite insufficient Finnish and missing networks as main hindrances, plus jobs where "Finnish is not required" but information exists only in Finnish ([TEK & IL, 2024](https://www.helins.fi/wp-content/uploads/2024/08/International-experts-2024-results.pdf)).

**6. International hiring is mostly uncertainty (P9).** The rules are knowable (specialist permit and EU Blue Card: €3,937/month in 2026, two-week fast track, [Migri](https://migri.fi/en/specialist)), yet employers treat "foreign" as a proxy for "paperwork", although many international jobseekers already live here with a right to work (assumption to validate with Espoo data). Since June 2025, people on work-based permits who lose their job have a 3- or 6-month protection period ([Migri](https://migri.fi/en/end-of-employment)): slow follow-up loses talent Finland already has.

**7. The public toolbox is under-sold and timing-sensitive (P1).** Espoo pays employers €5,000 for hiring an unemployed Espoo resident under 30 or a foreign-language speaker, but not if employment starts before the decision ([Espoo](https://www.espoo.fi/fi/rekrytointituki)). Pay-subsidy budgets vary by area ([Vates, 2025](https://vates.fi/palkkatuki-katkolla-monilla-tyollisyysalueilla-tilalle-kehitetty-uusia-rekrytointitukia/)), and the work trial exists for career clarification or return to work, not as a free try-out ([Act 380/2023, §54–55](https://www.finlex.fi/fi/lainsaadanto/2023/380)).

**What existing solutions get wrong:** matchmaking platforms keyword-match profiles (synthetic text to synthetic text) and leave the conversation itself unstructured, unrecorded and unfollowed. My features fix the conversation, not just the match.

## 2. Opportunity areas ("How might we…")

1. How might we turn a three-hour fair from a mass unstructured interview into a light, work-based signal generator without adding recruiter workload? (P3, P4, P6)
2. How might we get hiring managers' real needs (90-day outcomes, true language use, permit capability) three weeks before the event, not three days? (P2, P9)
3. How might we make genuine interest visible when AI makes applications free and benefit rules make them plentiful? (P4, P6, P1)
4. How might we give career changers, returners and internationals without Finnish networks the strong signals locals get from referrals and familiar employers? (P5, P10, P9)
5. How might we make the City's free service the lowest-risk way to hire by packaging public instruments and follow-through? (P1, P9)
6. How might we let companies that need an outcome, not an employee, meet freelancers and would-be entrepreneurs? (P2, P1, P5)

## 3. Feature ideas

### TAL-01: Role Reality Card (12-minute hiring-manager intake)
- **One-liner:** A guided hiring-manager intake that turns a wish-list ad into a Role Reality Card (three 90-day outcomes, at most three must-haves, real language use, permit stance) plus an evaluation kit, due 21 days before the event.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P2, P3, P10
- **How it works:** The organiser sends a link or runs the intake during Espoo's existing company visits. The manager answers by voice or text ("What must this person deliver by day 90?"), then plays a trade-off game: ten requirement cards, keep three. AI drafts the card, maps skills to ESCO, raises proxy alerts ("'5+ years' barely predicts performance; what should they be able to do?") and drafts the event kit: a 15-minute taster (TAL-06) and three structured questions (TAL-07). An Espoo specialist then does a 10-minute quality call. Cards approved by T-21 get pre-booked slots; late cards get walk-ins only.
- **What makes it new:** It productises the intake meeting recruiters run but SMEs skip, outputs an assessment kit instead of another ad, and gives companies a selfish reason to be early.
- **AI role & human-in-the-loop:** An LLM drafts; the manager decides every line; the organiser checks quality. No candidate data is involved.
- **Risks & mitigations (privacy, bias, legal):** Hallucinated requirements: line-by-line approval before publishing. Alerts are advisory; confidential roles can stay anonymous; only business contact data is processed.
- **48h prototype:** S — a messy synthetic ad with 11 requirements plus five answers becomes card, taster and questions in under a minute.
- **Real-world pilot notes:** Embed in the kick-off of Espoo's free tailored candidate search ([Espoo, 2026](https://www.espoo.fi/en/news/2026/05/how-your-business-doing-invite-us-visit)). KPIs: cards received ≥21 days ahead, must-haves before vs. after.
- **Self-assessment:** J1 5/5 · J2 3/5 · J3 5/5

### TAL-02: Language Reality Check
- **One-liner:** Replace "fluent Finnish required" with a task-level language map (task, language, CEFR level, day 1 or month 6) and show talent the support that closes the gap.
- **Journey stage:** Pre-event, During event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P2, P9, P10, P4
- **How it works:** In the intake (TAL-01) the manager places recurring tasks on a grid: "calls with Finnish drivers: Finnish speaking B1 by month 6", "safety instructions: English or Finnish reading B1 on day 1", "team meetings: English OK". The card shows an honest badge (English OK to start / Finnish learnable on the job / Finnish needed on day 1 for task X) and surfaces hidden requirements such as "internal documents only in Finnish". Talent self-assesses with the CEFR grid (no tests, no speech scoring) and sees the gap next to the support: workplace Finnish courses, IHH and City language services, and employer language-awareness coaching as in Espoo's 2026 internship pilot ([Espoo](https://www.espoo.fi/en/working-life/business-espoo-helping-companies-thrive/open-your-door-international-students-provide-summer-internship)). Booth staff can wear "Puhutaan suomea hitaasti" ("Let's speak Finnish slowly") badges.
- **What makes it new:** A binary filter becomes a time-phased requirement the company can justify (language is a protected ground under the [Non-Discrimination Act 1325/2014](https://www.finlex.fi/fi/lainsaadanto/2014/1325)), and hidden requirements finally surface.
- **AI role & human-in-the-loop:** Optional AI task suggestions from the old ad; the manager sets every level; talent levels are self-declared; nothing is inferred from names or nationality.
- **Risks & mitigations (privacy, bias, legal):** Inaccurate self-assessment: a self-selection aid, never a filter. Language data stays on the person's own profile; justifications stored with the role document proportionality.
- **48h prototype:** S — task grid and badge; a logistics role's "fluent Finnish" becomes "English to start, Finnish B1 by month 6 with a paid course".
- **Real-world pilot notes:** KPIs: roles whose requirement changed, foreign-language talent approaching them. Co-design with IHH.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### TAL-03: Sponsorship-First International Hiring
- **One-liner:** Companies state up front whether they can hire someone who needs a permit, each role gets an auto-generated permit-and-relocation pathway, and talent shares only a three-option right-to-work status, never nationality.
- **Journey stage:** Pre-event, During event, Post-event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P9, P10, P1, P4
- **How it works:** The company picks a stance: "can hire people needing an employer-based permit", "only people who already have the right to work", or "not sure, book IHH advice". A rules engine turns salary and duties into a plain-language pathway: specialist duties at ≥€3,937/month mean a specialist permit or EU Blue Card, a two-week fast track for first permits applied from abroad, and employer terms confirmed in Enter Finland within two working days ([Migri fast track](https://migri.fi/pikakaista)); below that, a permit for an employed person without fast track. Talent picks a status ("right to work, no employer action", "right to work with limits", "would need an employer-based permit"), revealed to a company only after mutual interest; the public stance lets talent self-select. After a match, one tap books [IHH employer advisory](https://ihhelsinki.fi/employers/), shares [Spouse Program](https://spouseprogram.fi/employers/) information and opens a relocation checklist.
- **What makes it new:** It flips the burden from guessing about candidates ("foreign = paperwork") to employer transparency, with official, dated rules at the moment of decision.
- **AI role & human-in-the-loop:** No AI: a versioned rules table linked to Migri. IHH and Migri remain the authorities; the company decides on hiring.
- **Risks & mitigations (privacy, bias, legal):** Outdated rules: annual update, visible source date, "information, not legal advice". The status is minimal, self-declared, revealed late and deleted 30 days after the event. City coaches, not companies, prioritise follow-up for people in a protection period.
- **48h prototype:** S — roles at €4,200 and €2,900/month yield different pathway cards; the status chip unlocks after "mutual interest".
- **Real-world pilot notes:** Co-own with IHH employer services. KPIs: roles with a declared stance, IHH consultations booked, offer-to-start time.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### TAL-04: Proof Stories & the Signal Ladder
- **One-liner:** Talent tells three two-minute "proof stories" in any language; AI suggests skills with the exact quote as evidence; the person confirms each, and every skill shows its evidence level: Told, Shown, Confirmed.
- **Journey stage:** Pre-event, During event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P5, P3, P6, P10, P1
- **How it works:** Guided STAR prompts ("A time you fixed something that kept breaking: what did you do, what changed?") are answered by voice or text in the person's strongest language. AI transcribes, translates and proposes ESCO skills linked to their source sentences; the person accepts, edits or rejects each and can add bridges (restaurant shift lead to logistics coordinator via scheduling). Skills start at Told, become Shown after a taster (TAL-06) and Confirmed when a company reviewer rates them against a rubric. Recruiters see ladder levels and original quotes, not polished prose. Aggregated counts (groups of 10+ only) feed a pre-event "pool preview" for hesitant companies (P1).
- **What makes it new:** AI extracts and translates evidence instead of polishing a CV, and provenance is explicit: Told is admitted to be weak, and everyone gets a free route to stronger signals.
- **AI role & human-in-the-loop:** Speech-to-text, translation and skill suggestions; the person confirms every skill; no scoring or ranking of people. RAI to confirm the AI Act classification.
- **Risks & mitigations (privacy, bias, legal):** Translation errors: original kept with a "machine-translated" label. Under-recognised care or informal work: optional coach review. Audio is deleted after transcription, with no voice or emotion analysis ([AI Act Art. 5(1)(f)](https://artificialintelligenceact.eu/article/5/)). Data comes from the person themself, as the [Working Life Privacy Act 759/2004](https://www.finlex.fi/fi/lainsaadanto/2004/759) prefers.
- **48h prototype:** M — synthetic "Olena", a former pharmacist aiming at QA roles, tells a story in Ukrainian, gets five suggested skills with quotes, rejects one and keeps four at Told.
- **Real-world pilot notes:** Run with Espoo career coaches; import the now-mandatory Job Market Finland profile to avoid double entry. KPIs: confirmed skills per profile, recruiter trust per ladder level.
- **Self-assessment:** J1 4/5 · J2 3/5 · J3 4/5

### TAL-05: Three Signals
- **One-liner:** Every talent gets exactly three "signals" per event to tell a company "you are my top choice", and companies get a limited number of invites: scarcity makes interest credible again when AI makes applications free.
- **Journey stage:** Pre-event, During event
- **Primary users:** Company, Talent
- **Pain points addressed:** P4, P6, P1
- **How it works:** When role cards go live (T-14), talent spends up to three signals with no cover letter, optionally attaching one proof story. Companies see signals in a separate lane ("12 signals" beside "140 interested") and must answer each by T-3 with a booked slot or "not this time" plus a redirect (TAL-08). Companies get a fixed number of invites per role (e.g., 10). Signals cannot be bought, transferred or topped up, and part of each booth's time stays reserved for walk-ins so signals never become a gate.
- **What makes it new:** It imports proven market design into public job fairs: the economists' job-market signal ([Coles et al., 2010](https://www.aeaweb.org/articles?id=10.1257/jep.24.4.187)) and US residency "program signals", where applicants had 2.7–9.1 times higher odds of an interview invitation from programmes they signalled ([JGME, 2024](https://doi.org/10.4300/jgme-d-24-00215.1)). AI can write a thousand applications; it cannot multiply three signals. Pilot question for Espoo: could a signal count towards the monthly job-search obligation, aligning compliance with intent?
- **AI role & human-in-the-loop:** No AI. People choose whom to signal; companies decide whom to meet.
- **Risks & mitigations (privacy, bias, legal):** Low digital confidence: multilingual explainer, coach help, one free undo. Signals hardening into requirements (a risk the [AAMC](https://www.aamc.org/services/eras-institutions/program-signaling-data) flags): reserved walk-in time and monitoring. Signals are visible only to the receiving company.
- **48h prototype:** S — talent spends a signal; the company dashboard splits Signals from Pool; a T-3 reminder for unanswered signals.
- **Real-world pilot notes:** Compare events with and without signals: recruiter-rated relevance, signal-to-next-step conversion, unanswered approaches.
- **Self-assessment:** J1 4/5 · J2 5/5 · J3 5/5

### TAL-06: Work-Sample Tasters
- **One-liner:** Each company publishes one 15-minute taster of the real job (re-plan six delivery routes after a truck breaks down, triage five support tickets, fix a broken spreadsheet), and the work becomes the introduction.
- **Journey stage:** Pre-event, During event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P3, P6, P5, P10
- **How it works:** The taster and a three-criterion anchored rubric ("finds the root cause / explains the trade-off / checks own work") are drafted from the Role Reality Card and approved by the hiring manager. At a "Taster Bar" (laptops plus paper versions), talent completes tasters for any company; submissions carry a code, not a name or photo. Reviewers rate them on their phones in about two minutes and tap "invite to talk". Each taster states its tool rule ("AI allowed, as in the job" or "no AI"), and every invitation opens with "walk me through your approach", so reasoning, not the artefact, is the signal. Remote participants get an online slot with a City host.
- **What makes it new:** It brings work samples (.33) and job knowledge (.40) into a format that runs on small talk (.19), and companies see the work before the name, countering the name penalty measured in Finland.
- **AI role & human-in-the-loop:** AI drafts tasters and rubrics; humans approve and rate. No AI grading in the MVP, as that would be high-risk candidate evaluation ([AI Act Annex III(4)](https://artificialintelligenceact.eu/annex/3/)).
- **Risks & mitigations (privacy, bias, legal):** Unpaid work: 15-minute cap, synthetic tasks only. Adverse impact (sizeable subgroup differences in US work-sample data, [Sackett et al. table](https://www.annualreviews.org/content/table/10.1146/annurev-orgpsych-020924-072127.t1)): plain language, a practice taster, extra time on request. Tasters stay job-content tasks, since personality or aptitude tests would trigger the consent and qualified-tester rules of Act 759/2004.
- **48h prototype:** M — synthetic Kuura Logistics route taster; candidate #A17 submits; the reviewer rates three anchors and taps "invite to talk"; the candidate gets a slot.
- **Real-world pilot notes:** One event, 8–10 companies. KPIs: taster-to-next-step vs. booth-only conversion, reviewer minutes per taster, participants' fairness rating.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### TAL-07: Seven-Minute Structured Conversations
- **One-liner:** Every booth conversation for a role uses the same three pre-announced questions with anchored rating scales on the recruiter's phone: the most predictive selection format we know, in seven minutes.
- **Journey stage:** During event
- **Primary users:** Company, Talent
- **Pain points addressed:** P3, P4, P10, P7
- **How it works:** The kit holds three questions (past behaviour, a situation, "walk me through your taster"), each with 1–5 anchors for weak, solid and strong answers, drafted from the Role Reality Card and approved by the hiring manager. Talent sees the topics in advance ("open book"), which helps non-native speakers and people without insider coaching. The recruiter app is one screen (timer, question, one-tap rating, one-line note) and works offline, so a Wi-Fi drop at opening time does not stop the booth (P8). Afterwards the company compares its own interviewers' ratings per role; there is no AI ranking.
- **What makes it new:** Structured interviews are the top predictor (.42 vs. .19 unstructured), yet as far as we know (assumption) no event platform structures the booth conversation itself. It fixes the "by conversation 15 I've forgotten conversation 3" problem every fair recruiter knows.
- **AI role & human-in-the-loop:** AI drafts questions and anchors only. No recording, transcription or voice/face analysis: emotion inference at work is prohibited (AI Act Art. 5(1)(f)). Humans rate and decide.
- **Risks & mitigations (privacy, bias, legal):** Recruiter resistance: three one-tap ratings and a 60-second calibration card. Ratings are the company's personal-data records: retention limit, candidate access on request. Residual bias: anchors and, where possible, two raters.
- **48h prototype:** S — recruiter phone UI with timer, questions, anchors and ratings; a comparison table of 12 synthetic conversations.
- **Real-world pilot notes:** KPIs: conversations per hour, inter-rater agreement where two recruiters share a booth, conversation-to-interview rate.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 5/5

### TAL-08: Redirect, Don't Reject
- **One-liner:** When a recruiter's answer is "not us", one tap sends the person, with consent and a one-line reason, to a better-fitting booth or City service, and every conversation gets closure within 48 hours.
- **Journey stage:** During event, Post-event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P4, P1, P10, P5
- **How it works:** After each conversation the recruiter taps Advance (next step and date), Redirect or Close. Redirect lists other role cards at the event, plus City services (Business Espoo advice, RekryKoulutus, language training), that share skill tags with the conversation; the recruiter picks one and writes why ("great with angry customers: try the telecom booth's support role"). If the person accepts, the receiving recruiter sees a "warm referral from Company A" badge. Close sends a respectful message within 48 hours with an optional rubric-based feedback line and a learning link. The organiser sees the funnel (conversations, next steps, redirects, hires at three months), its evidence for "is the City's pool any good?"
- **What makes it new:** Recruiters trust referrals more than CVs, and referred hires quit less ([Burks et al., 2015](https://doi.org/10.1093/qje/qjv010)), but referrals depend on networks international experts say they lack. This manufactures warm referrals for people without networks and turns the fair's many "no"s into routing.
- **AI role & human-in-the-loop:** Explainable tag overlap suggests targets; the recruiter chooses; the talent consents; closure messages need a human outcome tap. RAI to check the Annex III(4) boundary.
- **Risks & mitigations (privacy, bias, legal):** Data passing between employers: consent per redirect, as candidate data should come from the candidate or with their consent (Act 759/2004, §4). Hurtful feedback: vetted snippets only. Ignored 48-hour rule: reminders, and response rates affect priority slots next time.
- **48h prototype:** S — Redirect to Company B, talent accepts, referral badge appears in Company B's queue; plus a Close message preview.
- **Real-world pilot notes:** KPIs: share closed within 48 hours, redirect acceptance and conversion, talent agreement with "I knew where I stood".
- **Self-assessment:** J1 4/5 · J2 5/5 · J3 5/5

### TAL-09: Hire-Smarter Bundle
- **One-liner:** Each role card shows which public instruments could cut the cost and risk of the hire (Espoo recruitment support, youth recruitment support, pay subsidy, Espoo supplement, RekryKoulutus, IHH services), while a human advisor checks individual eligibility after mutual interest and before signing.
- **Journey stage:** Pre-event, Post-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P1, P9, P2
- **How it works:** A rules engine reads role-level facts (duration, working time, salary, training need) and lists what may apply, e.g., "12-month contract at ≥80% hours: €5,000 Espoo recruitment support possible if the hire is an unemployed Espoo resident under 30 or a foreign-language speaker" (full conditions linked), or "six-week skills gap: RekryKoulutus, employer pays 30% of training costs ([Suomi.fi](https://www.suomi.fi/palvelut/rekrykoulutus-keski-pohjanmaan-tyollisyysalue/07722e0b-46f1-4653-8e52-45113bc48949))". Nothing is shown per candidate. After Advance (TAL-08), "Check support before signing" opens a case for an Espoo employer-services advisor, who checks eligibility with the candidate's consent under a hard warning: "Don't sign yet: Espoo recruitment support cannot be granted if employment starts before the decision." The work trial appears only with its legal purpose (career clarification or return to work, max six months), never as a free try-out.
- **What makes it new:** It reframes "free, therefore low quality" as "the City de-risks your hire" ([Espoo](https://www.espoo.fi/fi/rekrytointituet)) and fixes the timing trap: employers often hear about support only after signing (assumption from practice).
- **AI role & human-in-the-loop:** No AI: rules plus a human advisor deciding for the authority.
- **Risks & mitigations (privacy, bias, legal):** Stigma ("subsidised = weak"): instruments attach to roles, never people. Eligibility attributes (age, mother tongue, unemployment duration) never enter matching. Budgets change (19 of 45 areas had paused pay subsidy in September 2025): "subject to availability" with an update date.
- **48h prototype:** S — role card, support panel, and a "Check before signing" button that creates an advisor ticket with the warning banner.
- **Real-world pilot notes:** KPIs: support checks requested and granted, days to decision, company satisfaction with the City service.
- **Self-assessment:** J1 4/5 · J2 3/5 · J3 5/5

### TAL-10: Project Lane
- **One-liner:** A parallel lane for companies' service needs (a three-month webshop rebuild, a part-time bookkeeper, a Ukrainian-speaking market study), matched with freelancers, light entrepreneurs and jobseekers ready to try self-employment, with Business Espoo advisors on the spot.
- **Journey stage:** Pre-event, During event, Post-event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P2, P1, P5
- **How it works:** The intake (TAL-01) opens with a fork: "Do you need an employee, or an outcome?" Outcome needs become Project Cards (deliverable, duration, budget band, "could become a job: yes/no"). Talent can mark "open to projects", including jobseekers curious about entrepreneurship. At a Project Corner, a Business Espoo advisor explains in ten minutes how to invoice (own company or light entrepreneurship), the start-up grant, and what self-employment means for unemployment benefit. Successful projects can convert into hires: the most realistic work sample there is.
- **What makes it new:** The brief names service needs, but fairs are built only for employment. With unemployment at 11.3% of Espoo's labour force in September 2026 ([City of Espoo](https://www.espoo.fi/fi/kaupunki-ja-paatoksenteko/tutkimus-ja-tilastot/tyossakaynti-tyopaikat-ja-tyottomyys)), many SMEs can buy an outcome long before committing to a hire; the lane links Business Espoo's entrepreneurship mission to recruitment.
- **AI role & human-in-the-loop:** AI drafts the Project Card from a free-text need; humans decide whom to talk to and contract with.
- **Risks & mitigations (privacy, bias, legal):** Disguised employment: a checklist (fixed hours, direction and supervision mean employment) flags cases to the advisor. Benefit consequences: advisor consult before any contract. Payment risk: a standard agreement template.
- **48h prototype:** S — intake fork, Project Card, Project Corner list and a bookable ten-minute Business Espoo consult.
- **Real-world pilot notes:** KPIs: Project Cards per event, projects started, project-to-hire conversions, businesses started via Business Espoo.
- **Self-assessment:** J1 3/5 · J2 4/5 · J3 4/5

## 4. My top 3 features (and why)

1. **TAL-06 Work-Sample Tasters**: the most direct answer to the challenge. When CVs are AI-written, the reliable signal is work done and reasoning explained live. It gives the organiser capability evidence it has never had (P3), makes booth traffic relevant (P4) and puts the name last (P10). TAL-07 is its cheap sibling; merge them for one "proof at the booth" feature.
2. **TAL-05 Three Signals**: the best novelty-to-effort ratio (no AI, half a day to build, market-design evidence). It separates genuine intent from compliance volume (P1, P4) without stigmatising anyone.
3. **TAL-01 Role Reality Card**: the upstream engine. Without real needs three weeks early (P2) nothing downstream works, and one intake yields the whole assessment kit. It plugs into Espoo's existing kick-off meetings, so it is pilotable next month.

If the team wants one P9 feature, take TAL-03: zero AI, high trust, and IHH as a ready partner.

## 5. Hero concept

**ProofDay: the Espoo job fair where the CV comes last.** TAL-01, TAL-05, TAL-06, TAL-07 and TAL-08 form one journey in which every step produces a stronger signal than a CV.

*T-21 days:* the operations manager of Kuura Logistics (a synthetic Espoo SME) builds her Role Reality Card in 12 minutes (TAL-01): three 90-day outcomes, "English to start, Finnish B1 by month 6", and a drafted taster and questions she approves.

*T-14:* Amina, a supply-chain planner who moved to Espoo with her spouse and already has the right to work, spends one of her Three Signals (TAL-05) on Kuura, with no cover letter.

*Event day:* at the Taster Bar she re-plans Kuura's delivery routes in 15 minutes (TAL-06); the reviewer sees only "#A17", rates three anchors and invites her to a seven-minute structured conversation (TAL-07). The recruiter taps Advance, and later redirects Mikko, a chef changing careers, to the food-tech booth (TAL-08).

*+48 hours:* every conversation has an outcome, and the City can show companies a funnel instead of a headcount.

Demo: three phones on stage (hiring manager, talent, recruiter), with TAL-02, TAL-03 and TAL-09 enriching the same card. Pitch line: "Espoo doesn't try to detect AI. It asks for proof."

## 6. Sources

- [Sackett et al. (2022), Journal of Applied Psychology](https://doi.org/10.1037/apl0000994)
- [Annual Reviews: selection validity comparison table](https://www.annualreviews.org/content/table/10.1146/annurev-orgpsych-020924-072127.t1)
- [Ladders (2018): recruiter eye-tracking study](https://www.theladders.com/career-advice/why-do-recruiters-spend-only-7-4-seconds-on-resumes)
- [Galdin & Silbert (2025), Making Talk Cheap](https://arxiv.org/abs/2511.08785)
- [Liang et al. (2023), GPT detectors are biased against non-native English writers](https://doi.org/10.1016/j.patter.2023.100779)
- [TEM: name-based hiring discrimination, 2016 vs. 2024](https://tem.fi/en/-/study-jobseekers-with-foreign-names-receive-fewer-employment-opportunities)
- [TEM: Nordic labour market service model](https://tem.fi/en/-/individual-services-to-support-job-search-in-the-nordic-labour-market-service-model)
- [Työmarkkinatori (2026): mandatory jobseeker profile](https://tyomarkkinatori.fi/uutiset/tyonhakuprofiilin-julkaisemisesta-velvoittavaa-poks)
- [City of Espoo (2026): employment situation, March 2026](https://espoo-sv.oncloudos.com/kokous/20261673-3-354122.PDF)
- [City of Espoo: unemployment statistics](https://www.espoo.fi/fi/kaupunki-ja-paatoksenteko/tutkimus-ja-tilastot/tyossakaynti-tyopaikat-ja-tyottomyys)
- [City of Espoo: recruitment support (€5,000)](https://www.espoo.fi/fi/rekrytointituki)
- [City of Espoo: employer subsidies overview](https://www.espoo.fi/fi/rekrytointituet)
- [City of Espoo (2026): tailored candidate search](https://www.espoo.fi/en/news/2026/05/how-your-business-doing-invite-us-visit)
- [City of Espoo (2026): international internship pilot](https://www.espoo.fi/en/working-life/business-espoo-helping-companies-thrive/open-your-door-international-students-provide-summer-internship)
- [Act on Organising Employment Services 380/2023](https://www.finlex.fi/fi/lainsaadanto/2023/380)
- [Vates (2025): pay subsidy pauses](https://vates.fi/palkkatuki-katkolla-monilla-tyollisyysalueilla-tilalle-kehitetty-uusia-rekrytointitukia/)
- [Suomi.fi: RekryKoulutus](https://www.suomi.fi/palvelut/rekrykoulutus-keski-pohjanmaan-tyollisyysalue/07722e0b-46f1-4653-8e52-45113bc48949)
- [Migri: specialist permit](https://migri.fi/en/specialist)
- [Migri: fast track](https://migri.fi/pikakaista)
- [Migri: end of employment](https://migri.fi/en/end-of-employment)
- [OECD (2025): Economic Survey of Finland, foreign talent](https://www.oecd.org/en/publications/oecd-economic-surveys-finland-2025_985d0555-en/full-report/enriching-human-capital-with-more-foreign-talent_5745d827.html)
- [TEK & IL (2024): International experts survey](https://www.helins.fi/wp-content/uploads/2024/08/International-experts-2024-results.pdf)
- [International House Helsinki: employers](https://ihhelsinki.fi/employers/)
- [Spouse Program: employers](https://spouseprogram.fi/employers/)
- [Burning Glass Institute & HBS (2024): Skills-Based Hiring](https://www.burningglassinstitute.org/research/skills-based-hiring-the-long-road-from-pronouncements-to-practice)
- [Coles et al. (2010), Journal of Economic Perspectives](https://www.aeaweb.org/articles?id=10.1257/jep.24.4.187)
- [JGME (2024): program signaling and interviews](https://doi.org/10.4300/jgme-d-24-00215.1)
- [AAMC: program signaling data](https://www.aamc.org/services/eras-institutions/program-signaling-data)
- [Burks et al. (2015), Quarterly Journal of Economics](https://doi.org/10.1093/qje/qjv010)
- [EU AI Act, Article 5](https://artificialintelligenceact.eu/article/5/)
- [EU AI Act, Annex III](https://artificialintelligenceact.eu/annex/3/)
- [Working Life Privacy Act 759/2004](https://www.finlex.fi/fi/lainsaadanto/2004/759)
- [Non-Discrimination Act 1325/2014](https://www.finlex.fi/fi/lainsaadanto/2014/1325)
