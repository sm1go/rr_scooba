# Round 1 Proposal — RAI (Responsible AI, Privacy & Legal Lead)

## 1. Problem analysis from my perspective

Both sides (S1, S2) increasingly let machines do their writing *and* their judging (P6). Between them sits a public body with statutory duties (S3). Four facts shape responsible design (C1, C3, C4).

**1. Ranking people is high-risk, and Finland already treats it that way.** [AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng) Annex III(4)(a) covers AI that places targeted job ads, filters applications or evaluates candidates. The Art. 6(3) derogation never applies to systems that profile people. Government proposal HE 108/2025 classifies the matching on Job Market Finland as high-risk because it ranks anonymous profiles using profiling ([Vantaa notice](https://www.vantaa.fi/en/processing-personal-data-job-seeker-profile-data-repository-and-ai-included-matching-functionality-service-platform-job-market-finland-when-processing-job-seeker-profiles)). The Digital Omnibus ([Reg. (EU) 2026/1744](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng), OJ 24 July 2026) moved the Annex III obligations to **2 December 2027**. The Art. 5 bans and the Art. 4 AI-literacy duty have applied since February 2025, and Art. 50 transparency since 2 August 2026 ([EP](https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/file-digital-omnibus-on-ai); [summary](https://pitch.law/academy/digital-omnibus-on-ai-regulation-2026-1744)). A 2027 pilot would run past that date. From then on, Espoo as a public deployer owes the Art. 26 duties (competent oversight, logs kept ≥ 6 months, informing the people affected), an Art. 27 fundamental-rights impact assessment (FRIA, which can cross-refer to the DPIA) and Art. 86 explanations. Since January 2026, fifteen Finnish authorities have supervised the Act under Act 1377/2025; the Data Protection Ombudsman covers Art. 5 ([tietosuoja.fi](https://tietosuoja.fi/-/uudet-saannot-vahvistavat-luottamusta-tekoalyyn-tekoalyasetusta-valvovien-viranomaisten-toimivaltuudet-tulivat-voimaan-1.1)). Under GDPR Art. 22, the [SCHUFA](https://curia.europa.eu/juris/liste.jsf?num=C-634/21) ruling treats a score that a third party "draws strongly on" as the decision itself. Hence: **no person-level scores.**

**2. Bias is measured, in both humans and machines.** In a Finnish field test using vacancies posted with the national employment service, Finnish-named applicants got 390 interview invitations per 1,000 applications; Somali-named applicants got 99 ([Ahmad 2020](https://doi.org/10.1111/soin.12276); [summary](https://blogit.metropolia.fi/tikissa/2022/08/18/nimi-leimaa-tyonhakijaa-asenteet-vaikeuttavat-maahanmuuttajien-tyollistymista/)). Embedding models used to retrieve résumés preferred white-associated names in 85.1% of tests and were also swayed by document length ([Wilson & Caliskan 2024](https://ojs.aaai.org/index.php/AIES/article/download/31748/33915)). Helsinki's anonymous-hiring pilot raised foreign-named applicants' interview probability by 5 percentage points, roughly closing the gap. When managers could choose whether to anonymise, the managers who opted in were not a random sample ([Kanninen et al. 2023](https://labore.fi/wp-content/uploads/2023/09/Tyopapereita-338.pdf)). Anonymity must therefore be the default.

**3. "Detecting AI" discriminates.** Seven GPT detectors flagged on average 61.3% of TOEFL essays by non-native writers as AI-written, yet the detectors were easy to evade ([Liang et al. 2023](https://www.cell.com/patterns/fulltext/S2666-3899%2823%2900130-7)). The [Non-Discrimination Ombudsman](https://yhdenvertaisuusvaltuutettu.fi/tyoelama) cites requiring perfect Finnish where the job does not need it as indirect discrimination. Fluency must never leak into matching (P10).

**4. Public employment services reshape incentives and lawful bases.** Jobseekers must usually apply for four jobs a month ([Job Market Finland](https://tyomarkkinatori.fi/en/personal-customers/search-for-work/job-seekers-customer-service-model/employment-plan)), and LinkedIn applications rose more than 45% in a year ([CNBC](https://www.cnbc.com/make-it/2025/10/29/recruiters-are-drinking-through-a-fire-hose-of-job-applications-experts-say.html)). Volume pays off more than quality. Since September 2026 jobseekers must publish an "anonymous" profile, which the authorities admit can be re-identified (Act 380/2023, ch. 14). Because the City also supervises benefits, consent is a weak lawful basis for its own processing (GDPR recital 43). Employers must collect only necessary data, collect it from the applicant directly, and use personality or aptitude tests only with consent and reliable methods ([Act 759/2004](https://www.finlex.fi/api/media/statute-foreign-language-translation/688410/mainPdf/main.pdf?timestamp=2004-08-12T21%3A00%3A00.000Z) ss. 3, 4, 13).

**What existing solutions get wrong:** event apps push for more meetings through opaque recommendations. Screeners reward polished writing, and detectors punish non-native writers. Compliance ends up as a PDF rather than as how the product behaves.

**Design patterns we must avoid**
- Person-level fit scores, rankings or "top candidate" lists.
- AI deciding admission or scarce slots without human review (C1).
- AI-text detectors or "authenticity scores".
- Emotion or engagement analytics from face, voice or video, which are banned in recruitment ([Commission guidelines](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-01/guide-prohibited_en.pdf)).
- Inferring personality or "culture fit".
- Scraping LinkedIn, GitHub or social media.
- CV, photo or video-CV intake; using name, age, nationality, native language, school prestige, dates or career gaps as features.
- Fluency or document length as hidden signals.
- Consent walls, pre-ticked sharing, indefinite retention.
- Reusing event behaviour for benefit supervision (GDPR Art. 5(1)(b)).
- Chatbots that do not disclose they are AI (Art. 50(1)).

## 2. Opportunity areas ("How might we…")

1. HMW let both sides meet on capability first and identity last? (P4, P10, P3)
2. HMW make AI a translator rather than a judge, in any language? (P5, P6, P9)
3. HMW replace AI detection with verifiable evidence of where each claim comes from? (P6, P3)
4. HMW prove the City's talent pool is relevant without exposing anyone? (P1, P2)
5. HMW keep participation voluntary for people on benefits while rewarding quality over volume? (P6, P10, P4)
6. HMW make fairness continuously tested and publicly visible? (P10, P1)

## 3. Feature ideas

### RAI-01: Reveal Ladder — double-blind capability cards until mutual interest
- **One-liner:** Both sides first meet as anonymous cards with no identity clues; identity is revealed step by step, and only after interest is mutual.
- **Journey stage:** Pre-event, During event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P4, P10, P3, P6
- **How it works:** There is no CV upload. Talent cards hold confirmed ESCO skills, evidence links, preferences, CEFR language levels and availability. There are no fields for name, photo, age, nationality, native language, schools or dates, and experience appears as durations, which hides gaps. Company need cards follow the same rules. A mutual star opens rung 1: first name, a meeting-slot request, and work-permit status shown next to the City's permit support (P9). After the meeting, only the talent can open rung 2 (contact details), shared through an offline QR pass that expires and keeps a sharing log (P8). An identifiability meter warns when fewer than five people in the pool share the card's attributes and suggests broader wording ("ex-Rovio" → "mobile games studio").
- **What makes it new:** Anonymous recruitment usually hides identity only at one screening step, and event apps reveal everything at once. The ladder works both ways, is staged and talent-controlled, and checks re-identification risk live.
- **AI role & human-in-the-loop:** AI only suggests ESCO tags and broader wording, and the talent confirms each one; the meter just counts. Every reveal is the person's own click (C1, C3).
- **Risks & mitigations (privacy, bias, legal):** Free text could re-identify people → free text is switched off at rung 0. Accessibility needs could stay hidden → an optional "adjustments needed" flag at rung 1. Legal anchors: GDPR Art. 5(1)(c) and 25(2); Act 759/2004 s. 3; Non-Discrimination Act s. 7. The thresholds are assumptions to confirm in the DPIA.
- **48h prototype:** M — two browser windows on synthetic data: mutual star → reveal; the meter turns green as the talent swaps an employer's name for a broader description.
- **Real-world pilot notes:** One tech event, with anonymity mandatory for all companies, because opt-in invites self-selection. KPIs: mutual-star rate, companies meeting at least one relevant person, interview invitations measured by an unlinked survey.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 5/5

### RAI-02: Mutual-Choice Scheduler — stable matching with a fairness floor (no AI)
- **One-liner:** Both sides choose whom they want to meet; a transparent stable-matching rule builds the schedule and guarantees every talent at least one conversation.
- **Journey stage:** Pre-event, During event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P4, P7, P10, P1
- **How it works:** A week before the event, talent rank up to five need cards. Companies rank anonymous cards (RAI-01) or open "anyone who picks us" slots. A deferred-acceptance (Gale–Shapley) algorithm with slot limits builds 15-minute meetings, so no pair who both prefer each other is passed over. Ties are broken by a published lottery seed, never by a score. A fairness floor then places every talent without a meeting into slots that companies have reserved. Organisers review and edit the result, all changes are logged, and schedules go out as calendar files stored on each device, which avoids the 9:00 login spike (P8).
- **What makes it new:** Meeting-request spam and opaque recommendations reward the loudest users. As far as we know, the market-design methods used for school-choice and medical-residency matching have not been used at public recruitment events. The rule can be explained in one sentence and involves no profiling.
- **AI role & human-in-the-loop:** No AI: people state preferences, the algorithm resolves conflicts and the organiser approves (C1). Systems that only apply rules written by people fall outside the AI Act's definition of an AI system (recital 12).
- **Risks & mitigations (privacy, bias, legal):** The schedule could be read as an automated decision under GDPR Art. 22 → inputs are people's own rankings, the organiser signs off, walk-in "open tables" stay available, and explanations are given on request ("Company X's six slots went to people it ranked higher; lottery #41"). Biased rankings → companies rank anonymous cards. Companies ranking too few people → a minimum number of open slots is a condition of taking part.
- **48h prototype:** S — about 100 lines of Python on 200 synthetic talents × 20 companies: the schedule, a before/after histogram of meetings, and a "why" pop-up.
- **Real-world pilot notes:** Compared with the last event: meetings rated relevant by both sides, talent with at least one meeting, no-shows.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 5/5

### RAI-03: Quote-Backed Cards — talent-owned AI interview with a no-inflation guard and provenance ribbons
- **One-liner:** A ten-minute interview in the talent's own language becomes skill claims tied to their own words, each labelled with where it came from; no AI detector ever checks them.
- **Journey stage:** Pre-event, During event
- **Primary users:** Talent, Company
- **Pain points addressed:** P5, P6, P9, P3
- **How it works:** Talent answer six behavioural questions by voice or chat in any supported language. The model proposes ESCO and transferable skills, each linked to a supporting quote. With no quote there is no claim, so "helped with Excel reports" cannot become "advanced analytics". The talent confirms, edits or deletes every line. A ribbon marks each line as *said*, *evidenced* (an artefact is attached) or *discussed live* (ticked by a rep, RAI-06), and need cards carry the same ribbons ("AI-drafted, confirmed by the hiring manager"). Companies read translated cards labelled as translations, so writing fluency stays invisible and language skills remain separate CEFR fields.
- **What makes it new:** AI CV tools optimise for impressiveness and feed the synthetic loop; this optimises for faithfulness. Using AI is treated as normal, and confirmation and evidence become the signal on both sides, which ends the detector arms race.
- **AI role & human-in-the-loop:** AI transcribes, translates and proposes; the talent decides on every line. It produces no score and is never used to filter people, yet it is built to high-risk standards until the DPIA/FRIA settles its classification. Art. 50(1) notice: "You are talking to an AI."
- **Risks & mitigations (privacy, bias, legal):** Speech recognition errors on accents → editable transcript, text option, accent testing in RAI-08. Hallucinated claims → no quote, no claim. Volunteered health or religion details → flagged for removal (GDPR Art. 9). Audio is deleted after transcription, hosting is in the EU, and user data is never used for training. Evidence that favours privileged careers → live demos and attestations from City advisers also count.
- **48h prototype:** M — chat with the persona "Amina, logistics coordinator, three-year caregiving gap"; the guard rejects an inflated claim, and the card renders with ribbons in Finnish and English.
- **Real-world pilot notes:** An adviser-assisted mode at City service points; a candidate for Finland's AI regulatory sandbox (due by August 2027). KPIs: "this card represents me" rating, share of evidenced claims.
- **Self-assessment:** J1 5/5 · J2 5/5 · J3 4/5

### RAI-04: Necessity Lint — fairness-checked need cards with a pool-impact preview
- **One-liner:** While a company drafts its need card, a checker flags requirements that are probably unlawful or exclude people without good reason, and shows how many registered people each one shuts out.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P2, P10, P1
- **How it works:** A hiring manager pastes an old ad or dictates the need, and AI drafts a structured card: six-month outcomes, must-have versus trainable skills, and the language level each task needs. The checker flags risky phrases with reasons tied to the Non-Discrimination Act and suggests measurable rewrites. Examples: "native Finnish" (a language requirement needs genuine, decisive job grounds, ss. 12–13), "young team" (age), "top university" (pedigree) and "no gaps" (career path); a typical rewrite is "customer calls in Finnish, CEFR B1". A pool bar shows the aggregate effect ("fluent Finnish: 64 → 9 cards; Finnish B1: 64 → 31"), as counts only, with k ≥ 10. Nothing is blocked.
- **What makes it new:** Inclusive-language checkers target gendered wording. We know of none tied to Finnish discrimination law or measuring exclusion against the actual pool. Compliance shows up as a bigger pool, and writing an early need card takes ten minutes.
- **AI role & human-in-the-loop:** City legal and equality experts curate the trigger rules, the LLM only explains and rephrases, and the company decides. No candidate data is processed; the counts come from RAI-05.
- **Risks & mitigations (privacy, bias, legal):** Mistaken for legal advice → framed as a "check", with the rulebook reviewed by City lawyers. Genuine requirements such as security clearance → a "justified" tag that talent can see. Alert fatigue → at most five hints. The checker supports the ban on discriminatory job ads (s. 17).
- **48h prototype:** S — a pasted ad with highlights, a reason-and-rewrite panel, and a live pool bar over 300 synthetic cards.
- **Real-world pilot notes:** Build and maintain the rulebook together with Espoo's equality planning. KPIs: need cards submitted at least 14 days before the event, requirements changed, change in pool size.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### RAI-05: Pool Proof — a k-anonymous preview of the City's talent pool
- **One-liner:** Weeks before an event, companies see privacy-safe evidence of the City's talent pool ("about 30 registered people combine Python, SQL and Finnish B1") and are invited to post a need card.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P1, P2, P3
- **How it works:** A public company page and the organiser dashboard show counts per skill cluster from registrations and, optionally, aggregates from the employment authority, never individual records. Cells below k = 10 are hidden, and counts carry stable rounding noise. A company types a need ("cloud DevOps, English OK"), sees the size of the matching pool and clicks "reserve a table", which opens the need-card flow (RAI-04). Organisers see gaps between supply and demand (for example, 40 analysts against three company needs) and focus outreach on the right companies.
- **What makes it new:** Today the objection "the City has no suitable candidates" is answered with anecdotes. Pool Proof answers it with evidence, using the disclosure-control methods of official statistics for employer outreach.
- **AI role & human-in-the-loop:** Optional AI maps needs to ESCO skills; counts are deterministic, and organisers choose what to publish. No output about any individual exists (C3).
- **Risks & mitigations (privacy, bias, legal):** Differencing attacks (comparing answers to similar queries) → a query budget per company and stable noise per cell. Purpose limitation → statistics and forecasting are listed purposes for employment-service customer data (Act 380/2023 s. 112); confirm with the KEHA Centre. Niche skills hidden below the threshold → a "fewer than 10 — talk to us" message routes the company to an adviser.
- **48h prototype:** S — a search page and heatmap over a synthetic pool, with visible "< 10" suppression and a reserve button.
- **Real-world pilot notes:** A/B-test event invitations with and without Pool Proof: sign-ups, first-time companies, how early need cards arrive.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### RAI-06: Glass Notes — structured, shareable conversation notes; AI transcribes, never judges
- **One-liner:** Reps note each conversation against the need card's criteria, the talent receives the same structured feedback, and no camera, microphone or emotion AI analyses anyone.
- **Journey stage:** During event, Post-event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P5, P4, P6, P3
- **How it works:** After each meeting the rep spends a minute ticking the criteria that were discussed or evidenced (this feeds the "discussed live" ribbon, RAI-03) and picking a next step: interview, keep in touch or not now. The rep can also dictate a memo of their own impressions, which is transcribed, mapped to the criteria and confirmed by the rep. Within 48 hours the talent receives feedback per criterion. Free-text notes are visible to the talent by default, since a GDPR access request would reveal them anyway. Organisers see only aggregates.
- **What makes it new:** Candidates at job fairs rarely get feedback. Notes that are shareable by default keep reps on job-relevant criteria (structured evaluation) and close the feedback loop, the opposite of video tools that score faces.
- **AI role & human-in-the-loop:** AI only transcribes the rep's memo and suggests which criterion each point belongs to; the rep confirms. Nothing analyses the candidate, because emotion recognition in recruitment is prohibited (Art. 5(1)(f)).
- **Risks & mitigations (privacy, bias, legal):** Reps may write less candidly → the ticks are the core of the note. Feedback may feel harsh → templates and a "not now" framing. Controller roles (City vs. company) are fixed in the participation terms (GDPR Art. 26 or 28). Retention follows the DPIA (assumption: six months).
- **48h prototype:** S — a mobile form for reps (ticks, next step, browser speech-to-text) plus a feedback inbox for talent.
- **Real-world pilot notes:** KPIs: talent receiving feedback within 48 h, usefulness as rated by talent, company follow-up rate.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### RAI-07: Voluntariness Firewall — event data never feeds benefit supervision; opt-in "count this as an application"
- **One-liner:** A technical and procedural wall keeps matchmaking data away from benefit supervision, while talent can choose to log a genuine event conversation toward their job-search obligation.
- **Journey stage:** Cross-cutting
- **Primary users:** Talent, Organizer
- **Pain points addressed:** P6, P10, P4
- **How it works:** Matchmaking runs in a separate data space with its own purpose and access roles. Employment advisers cannot see stars, declines or company notes, and the interface says so in eight languages. If the talent wishes, one tap exports a minimal record ("met Company X about role Y; next step: interview") to their own job-search log. A real conversation can then count toward the four-applications-a-month rule, which eases the pressure to mass-send AI-written applications. The lawful basis is documented for each data flow: the City's statutory task for its own service, and the talent's own initiative for anything shared or exported.
- **What makes it new:** Event platforms ignore the fact that in public employment services the organiser also supervises benefits. Making the separation explicit builds trust, and the export turns an incentive that breeds noise into one that rewards genuine conversations.
- **AI role & human-in-the-loop:** No AI. Advisers keep all benefit decisions, and the firewall stops event data being reused for other purposes.
- **Risks & mitigations (privacy, bias, legal):** Whether a conversation counts as applying for a job opportunity must be confirmed by Espoo's lawyers (assumption). Exports contain no notes, ratings or rejections. Consent is not the lawful basis for the City's core processing (GDPR recital 43), and purpose limitation applies (Art. 5(1)(b)).
- **48h prototype:** S — a data-flow diagram plus a talent screen with the promise banner and an "Add to my job-search log" button.
- **Real-world pilot notes:** Survey item "I felt free to take part"; number of exports; irrelevant approaches reported by companies.
- **Self-assessment:** J1 3/5 · J2 5/5 · J3 4/5

### RAI-08: Fairness Twin Lab — synthetic counterfactual audits as a release gate
- **One-liner:** Before every event and after every model or prompt change, each AI component is tested on synthetic twins that differ only in name, language background, education path or career gap, and the results are published.
- **Journey stage:** Pre-event, Cross-cutting
- **Primary users:** Organizer
- **Pain points addressed:** P10, P1, P3
- **How it works:** A generator creates twins with identical skills but names from the five origins in Ahmad's field test (Finnish, English, Russian, Iraqi, Somali). Further pairs differ only by a foreign degree, a three-year gap or B1-level writing. Every AI component (claim extraction, translation, ESCO tagging, need-card checks) runs on all twins. The lab reports flip rates, i.e. the share of pairs whose output changes when only the name changes, and impact ratios between groups. A release gate blocks deployment above thresholds set by the organiser (e.g., a flip rate over 1%), and a bulletin is published in the AI register (RAI-09).
- **What makes it new:** Fairness audits are usually one-off studies. This turns the field-test method into an automated check on every release, using synthetic data only (C2). No ethnicity data is needed, which matters because the AI Act's new Art. 4a permits special-category data for bias detection only where strictly necessary.
- **AI role & human-in-the-loop:** The lab tests the AI; people set thresholds, interpret results and decide whether to ship. Failures go to the product owner and the City's equality officer.
- **Risks & mitigations (privacy, bias, legal):** Twins miss real-world proxies → expert review plus an anonymous survey during the pilot. Name lists could stereotype → curated with community organisations. Passing does not prove fairness → several metrics and a qualitative review. Results feed Art. 9 risk management and the Art. 27 FRIA.
- **48h prototype:** M — 1,000 twin pairs run through our claim extractor, with a flip-rate dashboard; live, we swap "Amina Warsame" for "Anna Virtanen" and show identical output.
- **Real-world pilot notes:** Open-source the method for Helsinki, Vantaa and the national network of cities.
- **Self-assessment:** J1 3/5 · J2 5/5 · J3 5/5

### RAI-09: Glass Box — receipts, a contest button and a living AI register
- **One-liner:** Every AI suggestion carries a plain-language receipt (what was used, what was deliberately not used, and whom to contest it with). Every AI component has a public register card that also serves as the core of the DPIA and FRIA.
- **Journey stage:** Cross-cutting
- **Primary users:** Talent, Company, Organizer
- **Pain points addressed:** P10, P1, P7, P3
- **How it works:** Tapping ⓘ shows, for example: "Suggested because your confirmed 'SQL' and 'inventory planning' match two of three must-haves. Not used: name, age, nationality, native language, photo, school, dates." An "Is this wrong?" link lets the person correct their card or open a ticket with a named City adviser, who answers within three working days. Each component's register card lists purpose, AI Act classification and reasoning, data, oversight point, retention, Twin Lab results and a contact. It is generated from the system configuration, published in several languages and pre-fills the GDPR Art. 35 DPIA and the Art. 27 FRIA (C5).
- **What makes it new:** "Negative explanations" (what was not used) make the anti-bias design visible. Cards generated from configuration cannot drift from what the system actually does, and contests reach a person, not a chatbot.
- **AI role & human-in-the-loop:** Receipts are built from the deterministic matching inputs, not from after-the-fact LLM explanations. Humans resolve every contest, and logs are kept for at least six months (Art. 26(6)).
- **Risks & mitigations (privacy, bias, legal):** Information overload → one line by default, details on tap. Receipts revealing company criteria → agreed in the participation terms. Legal anchors: the Art. 26(11) duty to inform, the Art. 86 right to explanation, and GDPR Art. 15(1)(h) as read in [Dun & Bradstreet Austria](https://curia.europa.eu/juris/liste.jsf?num=C-203/22), which requires explaining the procedure and principles actually applied.
- **48h prototype:** S — the ⓘ pop-over, a contest form and a register card rendered from YAML.
- **Real-world pilot notes:** KPIs: contests per 100 users, resolution time, post-event trust score.
- **Self-assessment:** J1 3/5 · J2 3/5 · J3 5/5

## 4. My top 3 features (and why)

1. **RAI-01 Reveal Ladder.** It removes noise (P4) and bias (P10) at the source, and Finnish evidence shows that anonymity closes the interview gap. It is the privacy-by-design backbone for S1 and S2 (J1).
2. **RAI-02 Mutual-Choice Scheduler.** It replaces AI ranking of people with mutual human choice and a transparent rule. The result is less noise and a guaranteed conversation for every talent, with no high-risk classification, and it can be built in an afternoon (J1, J3).
3. **RAI-03 Quote-Backed Cards.** It is the only credible answer to P6 that does not punish non-native writers. It helps people speak for themselves (P5) and makes evidence, not polished prose, the signal (J2).

Honourable mention: RAI-08, our live J3 demo moment.

## 5. Hero concept

**Working name: "Mutual — signal without scores."** AI translates, people decide, and nobody is ranked.

Demo (synthetic data, C2): a cold-chain logistics SME pastes last year's job ad. Necessity Lint (RAI-04) flags "native-level Finnish"; rewording it as "Finnish B1 for customer calls" grows the event pool from 9 to 31 cards, three weeks before the event (P2). Amina, a logistics coordinator with a three-year caregiving gap, completes a ten-minute interview in English (RAI-03). Every claim on her card is backed by her own words, and the guard visibly refuses an inflated one (P5, P6). Both sides browse anonymous cards (RAI-01), and a mutual star reveals first names. The Mutual-Choice Scheduler (RAI-02) gives Amina two meetings and the SME four relevant conversations instead of a queue of cold approaches (P4). Finally, the organiser runs the Fairness Twin Lab (RAI-08) on 1,000 twins, swapping "Amina Warsame" for "Anna Virtanen", and shows the flip rate live against the release threshold (P10).

Closing line: no CV uploaded, no score shown, no decision left to AI, and the company met someone its old ad would have filtered out. Nothing ranks people, and everything is built to the high-risk standard that applies from 2 December 2027 (J3).

## 6. Sources

- [Regulation (EU) 2024/1689 — AI Act (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2024/1689/oj/eng)
- [Regulation (EU) 2026/1744 — Digital Omnibus on AI (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2026/1744/oj/eng)
- [European Parliament Legislative Train — Digital Omnibus on AI (adopted; OJ 24 July 2026)](https://www.europarl.europa.eu/legislative-train/theme-a-europe-fit-for-the-digital-age/file-digital-omnibus-on-ai)
- [pitch.law — "The Digital Omnibus on AI: What Regulation 2026/1744 Changed" (Nov 2026)](https://pitch.law/academy/digital-omnibus-on-ai-regulation-2026-1744)
- [European Commission — Guidelines on prohibited AI practices](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-01/guide-prohibited_en.pdf)
- [Regulation (EU) 2016/679 — GDPR (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2016/679/oj/eng)
- [CJEU C-634/21 SCHUFA Holding (Scoring), 7 Dec 2023](https://curia.europa.eu/juris/liste.jsf?num=C-634/21)
- [CJEU C-203/22 Dun & Bradstreet Austria, 27 Feb 2025](https://curia.europa.eu/juris/liste.jsf?num=C-203/22)
- [Data Protection Ombudsman — AI Act supervision powers in force 1 Jan 2026 (Finnish)](https://tietosuoja.fi/-/uudet-saannot-vahvistavat-luottamusta-tekoalyyn-tekoalyasetusta-valvovien-viranomaisten-toimivaltuudet-tulivat-voimaan-1.1)
- [Finlex — Act 380/2023 on the Organisation of Employment Services](https://www.finlex.fi/en/legislation/2023/380)
- [City of Vantaa — job seeker profiles and AI matching on Job Market Finland (HE 108/2025)](https://www.vantaa.fi/en/processing-personal-data-job-seeker-profile-data-repository-and-ai-included-matching-functionality-service-platform-job-market-finland-when-processing-job-seeker-profiles)
- [Job Market Finland — employment plan and job search obligation](https://tyomarkkinatori.fi/en/personal-customers/search-for-work/job-seekers-customer-service-model/employment-plan)
- [Act on the Protection of Privacy in Working Life 759/2004 — unofficial English translation](https://www.finlex.fi/api/media/statute-foreign-language-translation/688410/mainPdf/main.pdf?timestamp=2004-08-12T21%3A00%3A00.000Z)
- [Non-Discrimination Ombudsman — working life (Finnish)](https://yhdenvertaisuusvaltuutettu.fi/tyoelama)
- [Ministry of Justice — equality assessment: Non-Discrimination Act ss. 10, 13, 17 (Finnish)](https://yhdenvertaisuus.finlex.fi/yhdenvertaisuuden-arviointi/mita-arvioidaan/)
- [Ahmad (2020), "When the Name Matters", Sociological Inquiry](https://doi.org/10.1111/soin.12276)
- [Metropolia blog — Ahmad's callback figures (Finnish)](https://blogit.metropolia.fi/tikissa/2022/08/18/nimi-leimaa-tyonhakijaa-asenteet-vaikeuttavat-maahanmuuttajien-tyollistymista/)
- [Kanninen, Kiviholma & Virkola (2023), "Anatomy of an Anonymous Hiring Pilot", Labore Working Paper 338](https://labore.fi/wp-content/uploads/2023/09/Tyopapereita-338.pdf)
- [Wilson & Caliskan (2024), "Gender, Race, and Intersectional Bias in Resume Screening via Language Model Retrieval", AIES](https://ojs.aaai.org/index.php/AIES/article/download/31748/33915)
- [Liang et al. (2023), "GPT detectors are biased against non-native English writers", Patterns](https://www.cell.com/patterns/fulltext/S2666-3899%2823%2900130-7)
- [CNBC (Oct 2025) — LinkedIn applications up more than 45% in a year](https://www.cnbc.com/make-it/2025/10/29/recruiters-are-drinking-through-a-fire-hose-of-job-applications-experts-say.html)
