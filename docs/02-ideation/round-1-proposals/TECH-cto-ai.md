# Round 1 Proposal — TECH (CTO & AI/ML Lead)

## 1. Problem analysis from my perspective

**The synthetic-signal loop (P6) is a representation problem, not a detection problem.** LinkedIn applications grew ~45% in a year to ~11,000 per minute, with generative AI a key driver ([Ars Technica, reporting NYT data](https://arstechnica.com/ai/2025/06/the-resume-is-dying-and-ai-is-holding-the-smoking-gun/)). When LLMs write CVs and LLMs read them, prose similarity rewards keyword stuffing. Detection is a dead end: OpenAI withdrew its own AI-text classifier for its "low rate of accuracy" (26% true positives, worse outside English) ([OpenAI](https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/)), and seven popular detectors flagged on average 61.3% of human-written non-native English essays as AI ([Liang et al., 2023](https://www.cell.com/patterns/fulltext/S2666-3899%2823%2900130-7)). In Espoo, where 25.9% of residents are foreign-language speakers ([City of Espoo](https://www.espoo.fi/fi/kaupunki-ja-paatoksenteko/tutkimus-ja-tilastot/vaesto)), a detector would be a discrimination engine (P10). **So: let people use AI to express themselves, but make prose irrelevant to outcomes** — decide on signals that are costly to fake: checkable specifics, artefacts, structured live conversation, witnessed demonstration, scarce intent.

**Selection research agrees.** Structured interviews are the strongest predictor of job performance (ρ ≈ .42), ahead of job-knowledge tests (.40) and work samples (.33); unstructured interviews reach .19 and years of experience .07 ([Sackett et al., 2022](https://doi.org/10.1037/apl0000994)). Today's event is a room of unstructured interviews; we can make it a room of 8-minute structured ones.

**A shared language exists — but never auto-tag people.** ESCO v1.2 has 3,039 occupations and 13,939 skill/knowledge concepts in 28 languages, via web or local API ([ESCO](https://esco.ec.europa.eu/system/files/2024-05/V1.2%20Launch%20-%20ESCO%20SEC%20combined%20-%20final%20clean.pdf), [ESCO API](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-api)); Job Market Finland already encodes postings in FINESCO, its ESCO extension ([API docs](https://tyomarkkinatori.fi/jobposting-new/documentation/KIPA-manage-jobpostings-en.html)). Yet extraction is brittle: in the service's own experiment, embedding search mapped "I can help with using a wheelchair" to "advise customers on the use of glasses" ([Työmarkkinatori blog](https://tyomarkkinatori.fi/blogit/vieraskyna-niittyla-tekoalyn-hyodyntaminen-esco-osaamisten-haussa)). AI suggests; the person confirms; unmapped skills stay free text.

**What existing approaches get wrong.** (a) One opaque score per person: Job Market Finland ranks suggestions by a calculated score that deducts points for language, education and location mismatch ([Job Market Finland](https://tyomarkkinatori.fi/en/instructions-and-support/personal-customers/instructions-for-the-my-job-path-section/independent-job-search/how-the-matching-works)) — exactly the dimensions P10 warns about. (b) First-come slot booking at doors-open: the P8 spike *and* a race won by people with free time and fast connections. (c) AI video-interview scoring — emotion recognition on candidates is now prohibited (AI Act Art. 5(1)(f); [Commission guidelines](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-01/guide-prohibited_en.pdf)).

**Regulation as architecture (C1, C3, C4).** AI that filters applications or evaluates candidates is high-risk (Annex III(4)(a)) and the Art. 6(3) exemption never covers profiling ([AI Act](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)); under the Digital Omnibus (Regulation (EU) 2026/1744) these duties apply from 2 December 2027 ([Council](https://www.consilium.europa.eu/en/press/press-releases/2026/05/07/artificial-intelligence-council-and-parliament-agree-to-simplify-and-streamline-rules/), [Bratby Law](https://bratby.law/digital-omnibus-ai-high-risk-delay/)) — just when a pilot would scale. A score a third party "draws strongly" on can itself be an Art. 22 GDPR decision ([CJEU C-634/21](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A62021CJ0634)), and explanations should show how different data would change the result ([CJEU C-203/22](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A62022CJ0203)). Design rules: (1) **rank needs, not people**; (2) **ML on public data, deterministic logic on personal data**; (3) **every AI output is a suggestion its subject confirms**, logged in a hash-chained ledger; (4) **symmetric, counterfactual explanations**; (5) **no biometric, voice or emotion inference.**

**P8 is self-inflicted:** everyone authenticates and books in the same minute. Pre-scheduled, signed, offline-cached agendas make doors-open a static-file problem a CDN solves.

**Suggested stack & build plan.** SvelteKit PWA (Workbox, Dexie/IndexedDB for the on-device passport, `jose` Ed25519 for passes and VC-JWT credentials); thin API on EU-region Postgres (SQLite for the demo) with the ledger and 30-day event-data expiry (to confirm with RAI). Python prep: ESCO v1.2 CSVs → sector subset → bridge table from occupation–skill co-occurrence and `multilingual-e5` embeddings of *public* labels. LLM: JSON-schema-constrained calls to EU-hostable open-weight models — Poro 2 for Finnish/English ([AMD Silo AI](https://www.amd.com/en/blogs/2025/silo-ai-continued-pretraining-provides-blueprint-for-gla.html)), EuroLLM-22B for 35 languages ([EuroLLM](https://huggingface.co/blog/eurollm-team/eurollm-22b)) — via vLLM/Ollama; Whisper for speech. Synthetic data (C2): seeded generator → 40 companies, 300 personas in fi/sv/en/ar/uk with "plain" and "AI-polished" twins. Plan: H0–6 data, schemas · H6–18 Need Compiler, passport · H18–28 matcher, Fit Sheet, bridges · H28–36 tokens, scheduler, pass, offline check-in · H36–42 agenda, rubric, credentials · H42–48 load test, pitch.

## 2. Opportunity areas ("How might we…")

- HMW make AI-polished prose irrelevant by anchoring every claim to evidence a human can check? (P6, P5, P3)
- HMW turn a vague, late company need into a concrete, bias-linted Need Card in ten minutes — and instantly show whether the City's pool can meet it? (P2, P1, P10)
- HMW match people and opportunities without ever ranking people? (P4, P10, P3)
- HMW turn event minutes into hard-to-fake, portable evidence? (P6, P4, P9)
- HMW make doors-open a non-event for servers and a fair start for everyone? (P8, P7)
- HMW test fairness without collecting a single sensitive attribute? (P10, P3)

## 3. Feature ideas

### TECH-01: Need Compiler
- **One-liner:** A hiring manager talks for ten minutes in any language; the system compiles an ESCO-structured Need Card, lints it for proxy requirements and test-runs it against the registered pool.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P2, P1, P10, P4
- **How it works:** An LLM interviewer (disclosed as AI, Art. 50) asks what a good recruiter would: 3–6-month outcomes, must-haves vs. trainable skills, where Finnish is needed and at what CEFR level, permit support — and "what would convince you in an 8-minute conversation?" (the evidence question). Constrained decoding fills a JSON schema with ESCO URI suggestions (local ESCO API search + embedding rerank). A rule-based linter flags proxies — "5+ years" (validity .07), "native Finnish", "Finnish degree" — and proposes task- or evidence-based rewrites; a test run against TECH-10 shows how each must-have shrinks the pool. The published card is non-personal data, exportable to Job Market Finland's Jobposting API (FINESCO).
- **What makes it new:** Needs treated like code — compile, lint, test, ship — with *proof* defined up front, which no intake form asks.
- **AI role & human-in-the-loop:** AI interviews and drafts; the deterministic linter explains itself; the manager accepts, edits or rejects every line (logged). Warnings never block; overrides stay visible.
- **Risks & mitigations (privacy, bias, legal):** Role data, not talent data. Hallucinations → nothing publishes unconfirmed, with a "you said / we compiled" diff. EU-hosted open-weight model, no prompt retention.
- **48h prototype:** M — a 60-second Finnish voice memo becomes an English Need Card with ESCO must-haves, an evidence question and a lint warning; editing "native Finnish" to "Finnish B1 for customer calls" moves the TECH-10 band.
- **Real-world pilot notes:** Business Espoo client managers book the call 2–3 weeks out; needs freeze at T-7 — only published cards get pre-matched requests. KPI: companies with confirmed needs at T-7.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### TECH-02: Evidence-Linked Skill Passport
- **One-liner:** Talent tell 3–5 work stories by voice or text in their own language; AI proposes ESCO skills, each pinned to the sentence that supports it, and the person confirms what is true.
- **Journey stage:** Pre-event, Post-event
- **Primary users:** Talent, Organizer
- **Pain points addressed:** P5, P6, P3, P10
- **How it works:** Whisper transcribes answers to prompts like "Tell me about a time something broke and you fixed it"; the LLM returns claims as `{esco_uri, quote_span}`, and a deterministic guard drops any claim whose quote is not in the transcript. A specificity coach asks follow-ups that make claims checkable — which system, how many people, what changed — instead of asking "did AI write this?". Each confirmed claim carries an evidence level (*claimed → specifics → artefact → witnessed*); a pasted AI-written CV yields only "claimed" suggestions, so polish buys nothing. The passport lives in IndexedDB on the device and exports as a signed file.
- **What makes it new:** Evidence-graded, span-grounded claims instead of a CV; specificity, not authorship, as the quality bar — which helps non-native speakers rather than penalising them.
- **AI role & human-in-the-loop:** AI transcribes, suggests and asks; only the person confirms. Rejected suggestions are discarded.
- **Risks & mitigations (privacy, bias, legal):** Sensitive details in stories → transient EU-hosted processing, no retention, local redaction. Language-dependent extraction → TECH-11 parity tests. Speech recognition for e.g. Farsi or Albanian is an untested assumption; typed and coach-assisted entry remain.
- **48h prototype:** M — an Arabic-speaking persona dictates a story; claims appear with highlighted source quotes; she rejects one, edits another; DevTools shows no server copy.
- **Real-world pilot notes:** City career coaches guide people with low digital skills, with live consent on the person's own device. KPI: claims at "specifics" or above per person.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### TECH-03: Bridge Finder
- **One-liner:** Shows career changers the explicit ESCO path from what they have proven to what a company needs — and lets them confirm whether the bridge is real.
- **Journey stage:** Pre-event
- **Primary users:** Talent, Company
- **Pain points addressed:** P5, P10, P3, P4
- **How it works:** From public ESCO data only, we precompute a bridge table of skill pairs scored by shared parent in the skill hierarchy, co-occurrence as essential skills across occupations (Jaccard) and multilingual embedding similarity, each with a readable rationale. On the talent's device, each uncovered must-have triggers a prompt, e.g. (illustrative labels) "Your *schedule shifts* skill is close to *plan resource allocation* — give one example of planning people against demand." Only bridges confirmed with a short story reach companies, labelled "transferable — probe in conversation".
- **What makes it new:** Transferable skills as auditable graph paths plus a human story, not a hidden similarity score; the table is public, versioned and City-curated.
- **AI role & human-in-the-loop:** Embeddings touch only public taxonomy text; talent decide whether a bridge is true, companies whether it matters; organisers curate the table.
- **Risks & mitigations (privacy, bias, legal):** Stereotyped routes (e.g., into lower-paid work) → bridges are skill-to-skill, never demographic, and TECH-11 audits routing per persona group.
- **48h prototype:** S — bridge table for ~400 skills; a former restaurant shift lead confirms one of three bridges into a logistics need, and the company sees its rationale.
- **Real-world pilot notes:** Co-curate with Espoo's sector advisers; publish as open data. KPI: next-step rate of bridge-based vs. direct matches.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 4/5

### TECH-04: Rank Needs, Not People
- **One-liner:** Company needs are published as a signed public catalog; each talent's browser computes which needs fit them, so the City never computes, stores or shows a ranking of people.
- **Journey stage:** Pre-event, During event
- **Primary users:** Talent, Company, Organizer
- **Pain points addressed:** P4, P6, P10, P8, P3
- **How it works:** Need Cards plus the relevant bridge-table slice form a small catalog (estimate: under 300 KB), signed with the organiser's Ed25519 key and served from a CDN. The PWA verifies it and matches locally and deterministically: per must-have, exact ESCO match → hierarchy match → confirmed bridge → gap, with location and permit-support filters the talent toggles. The talent reads Fit Sheets (TECH-05) and chooses whom to approach (TECH-08); only then are the relevant claims sent under an event-scoped pseudonym, with names revealed after mutual acceptance. Company "open calls" surface only on devices where they match.
- **What makes it new:** It inverts the platform: computation moves to the data subject, so central profiling disappears by design — and matching has no server to crash at peak.
- **AI role & human-in-the-loop:** No ML at match time. Talent decide whom to approach, companies whom to meet; inboxes are grouped by need and shuffled, never sorted by fit; recruiter filters are explicit, logged choices.
- **Risks & mitigations (privacy, bias, legal):** Tampering → signatures. Gaming the matcher is pointless: it only advises the talent, and companies see evidence-levelled claims probed live. Pool insight → aggregates only (TECH-10). Assumption for RAI: deterministic matching may fall outside the AI Act's "AI system" definition; we still build to Annex III standards (C1, C3, C4).
- **48h prototype:** M — 40 Need Cards matched in the browser; the network tab shows zero passport bytes leaving the device until "Request conversation".
- **Real-world pilot notes:** Publish the catalog as open data for existing event platforms. KPI: company-rated share of irrelevant approaches vs. a previous event.
- **Self-assessment:** J1 4/5 · J2 5/5 · J3 5/5

### TECH-05: Fit Sheet
- **One-liner:** A score-free, one-page explanation of each talent–need pairing that both sides see identically, including the smallest change that would alter the result.
- **Journey stage:** Pre-event, During event
- **Primary users:** Talent, Company
- **Pain points addressed:** P4, P5, P10, P3
- **How it works:** Deterministic code renders, per must-have, a status (*witnessed / artefact / specifics / claimed / bridge / gap*) with an evidence pointer, plus logistics and the language requirement as a task ("customer calls in Finnish: B1") beside the self-declared level — language is never inferred from writing quality. A counterfactual line names the smallest change to full coverage ("add evidence for *SQL*, e.g. at the Proof Booth"); the company version shows which of *its* requirements blocks most requests. Optional LLM paraphrases into the reader's language are labelled, with the authoritative original one tap away — Espoo's own AI-translation experiment concluded that AI suits clear content and that trust must be built ([City of Espoo](https://www.espoo.fi/en/news/2026/09/espoos-ai-translation-experiment-has-ended)).
- **What makes it new:** No percentages, no hidden assessment: what the company sees is what you see. Counterfactuals turn an explanation into an action plan, in the spirit of C-203/22.
- **AI role & human-in-the-loop:** No AI in the logic; optional, labelled paraphrase. Humans read and decide.
- **Risks & mitigations (privacy, bias, legal):** Statuses misread as grades → they describe evidence *type*, not quality; no aggregate score exists anywhere. The sheet holds only what the talent chose to share.
- **48h prototype:** S — one Fit Sheet in Finnish for the recruiter and Ukrainian for the talent, with the counterfactual toggle.
- **Real-world pilot notes:** 30-second comprehension test with five recruiters and five talent. KPI: share of conversations both sides rate "relevant".
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### TECH-06: Proof Conversations
- **One-liner:** Every booked conversation gets a shared agenda from the Fit Sheet and the company's evidence question, plus a one-tap anchored rubric — turning event chit-chat into the most predictive selection format we know.
- **Journey stage:** During event, Post-event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P4, P6, P3, P5
- **How it works:** Both sides get the agenda 24 h ahead: the need in one line, two must-haves to probe with the evidence question, a 2-minute "show me" (walk through an artefact, sketch a solution or do a tiny live task) and next steps. Talent may prepare — even with AI — because live follow-ups test understanding. The recruiter taps per must-have *not covered / described / specific / demonstrated*; nothing is recorded. Afterwards the company picks "next step" or "not now" with a reason code pointing to a need item, and the talent gets a structured feedback card; organisers see only per-need aggregates (e.g., 12 talks, none "demonstrated" for Kubernetes) as a skills-gap signal.
- **What makes it new:** Structured interviewing mass-produced at a matchmaking event, generated from both sides' data — it should move conversations from the unstructured (.19) toward the structured (.42) validity range at near-zero cost.
- **AI role & human-in-the-loop:** Deterministic agenda template, optional LLM phrasing; humans converse, rate evidence and decide. No emotion, voice or face inference (Art. 5(1)(f)).
- **Risks & mitigations (privacy, bias, legal):** Rubric becoming a person score → it rates evidence per need item, is visible to the talent and never aggregated across companies. Feedback liability → reason codes cite only job-related need items. Rater drift → a calibration card per need.
- **48h prototype:** S — agenda card, 8-minute timer, offline four-level rubric and the talent's feedback card.
- **Real-world pilot notes:** 15-minute recruiter briefing; online, the agenda sits beside the video call. KPI: next-step rate; "relevant conversation" ratings from both sides.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 5/5

### TECH-07: Witnessed-Skill Credentials
- **One-liner:** When a practitioner witnesses a skill live — in a Proof Conversation or at a City "Proof Booth" — the talent receives a signed, portable credential they own.
- **Journey stage:** During event, Post-event
- **Primary users:** Talent, Company, Organizer
- **Pain points addressed:** P6, P3, P9, P10, P1
- **How it works:** A witness — a company engineer, or a volunteer practitioner at a booth running 15-minute task cards (pair-debugging, a spreadsheet model, a customer call in Finnish) — taps "witnessed" on one specific claim. The backend issues a W3C Verifiable Credential 2.0 ([W3C](https://www.w3.org/TR/vc-data-model-2.0/)) in Open Badges 3.0 style: issuer City of Espoo, witnessing organisation, ESCO URI, task card, date — no grade. Anyone can verify it via QR (signature plus revocation status list); it upgrades the claim in future Fit Sheets, building a cross-event track record no generator can backdate. The format targets EUDI Wallets, which Member States must offer by end-2026 ([eIDAS 2.0](https://eur-lex.europa.eu/eli/reg/2024/1183/oj), [timeline](https://www.virtualbadge.io/blog-articles/eidas-2-0-eudi-wallet-what-digital-credentials-must-be-able-to-do-now)).
- **What makes it new:** It turns the one signal AI cannot fake — a live, human-witnessed demonstration — into durable evidence from a public issuer. For internationals with hard-to-read foreign degrees, "witnessed in Espoo" beats pedigree.
- **AI role & human-in-the-loop:** No AI. A named human witness decides; the holder decides whether to keep, show or delete.
- **Risks & mitigations (privacy, bias, legal):** Inconsistent standards → per-skill task cards with pass descriptors; the credential says "witnessed, not certified". No negative credentials: a failed attempt leaves no trace. Booths are optional; City legal reviews issuer wording.
- **48h prototype:** S — the witness taps on phone A, the credential lands on phone B, phone C verifies it (demo key).
- **Real-world pilot notes:** Start with three task cards in high-demand areas; witnesses from participating companies deepen their engagement (P1). KPI: next-step rate where a must-have is witnessed.
- **Self-assessment:** J1 4/5 · J2 5/5 · J3 4/5

### TECH-08: Intent Tokens
- **One-liner:** Each talent has five priority requests per event, each tied to one need item and one piece of evidence; companies get a capped invitation budget — scarcity restores signal.
- **Journey stage:** Pre-event, During event
- **Primary users:** Talent, Company
- **Pain points addressed:** P4, P6, P5
- **How it works:** Bookmarks are free and private; a priority request costs one token and two taps — "which need item", "which evidence" — plus an optional 200-character note instead of a cover letter. Tokens are refunded if the company declines within 24 h or never answers, and each Need Card shows the company's past response rate — a behavioural signal over time that AI cannot polish. Companies see requests grouped by need item and shuffled; their own budget (e.g., 15 invitations) stops them blasting the pool. Budgets are equal for everyone.
- **What makes it new:** Market-design signalling for municipal matchmaking: the AEA's economics job market caps candidates at two "special interest" signals, with survey evidence that this facilitated matches ([Coles et al., 2010](https://www.aeaweb.org/articles?id=10.1257/jep.24.4.187)). Applying is free for an AI agent; spending a scarce token is not.
- **AI role & human-in-the-loop:** No AI. Talent and companies choose.
- **Risks & mitigations (privacy, bias, legal):** Less confident talent under-using tokens → coaches and Fit Sheets point to "safe bets"; budget effects reviewed per event in aggregate. Multiple accounts → one pass per registration; duplicates handled by staff, never biometrics.
- **48h prototype:** S — token counter, request flow with refund on decline, company inbox grouped by need.
- **Real-world pilot notes:** Calibrate budgets to event size; publish the rules in plain language. KPI: company-rated relevance of approaches; 24-hour response rate.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### TECH-09: Peak-Proof Event Pass
- **One-liner:** Humans pick who, the machine picks when: agendas are scheduled before the event, signed into an offline QR pass and cached in a PWA — no login storm, no race for slots.
- **Journey stage:** Pre-event, During event
- **Primary users:** Organizer, Talent, Company
- **Pain points addressed:** P8, P7, P4
- **How it works:** When the request window closes (T-48 h), companies have accepted specific pairs; a deterministic scheduler (greedy plus OR-Tools CP-SAT) assigns times and tables, maximising first the number of people with at least one meeting, then total meetings — it judges no one. Each person gets an Ed25519-signed QR token (pseudonymous event ID, agenda hash) and a PWA caching agenda, map, catalog and Fit Sheets — no install, no password: the pass is the login. Staff phones verify passes offline and append check-ins to an idempotent local log that syncs later. Online rooms are pre-created, join links travel inside the pass and cohorts start at staggered 3-minute offsets; walk-ins join standby queues via a venue QR.
- **What makes it new:** It removes the root cause of P8 instead of buying bigger servers, and makes robustness and fairness one fix — no first-come advantage for faster connections.
- **AI role & human-in-the-loop:** No AI; transparent slot optimisation only. Organisers can override any slot.
- **Risks & mitigations (privacy, bias, legal):** Lost phone → printable pass. Replay → one staff-confirmed check-in per pass. Per-event pseudonyms prevent cross-event tracking (C3).
- **48h prototype:** M — k6 recording of 5,000 virtual users hitting CDN-served passes at T0, plus live check-in in airplane mode.
- **Real-world pilot notes:** Export agendas as ICS plus pass for any platform. KPI: p95 latency and errors at doors-open; share of attendees with at least one meeting.
- **Self-assessment:** J1 3/5 · J2 3/5 · J3 5/5

### TECH-10: Supply Radar
- **One-liner:** While drafting a need, a company sees banded, k-anonymous counts of registered attendees with confirmed or evidenced must-haves — and which requirement shrinks the pool most.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P1, P2, P3, P10
- **How it works:** Talent may opt in to contribute confirmed ESCO URIs and evidence levels — no names, no free text, a fresh random ID per event — to an aggregate pool. The radar answers only queries generated from a Need Card draft (at most three must-haves combined), returns bands (<5, 5–9, 10–19, 20+) with suppression below k = 5, and is rate-limited and logged against differencing attacks. A company sees, e.g., "Python + data visualisation: 10–19 claimed, 5–9 witnessed; adding 'Finnish C1': <5". Organisers see aggregates across all needs and target outreach before the event.
- **What makes it new:** It answers the City's hardest objection (P1: "your pool has no suitable candidates") with live, privacy-preserving evidence, and makes early need submission instantly rewarding (P2).
- **AI role & human-in-the-loop:** No AI at query time — counts only. Companies and organisers decide what to change.
- **Risks & mitigations (privacy, bias, legal):** Re-identification in small pools → k-threshold, bands, fixed query shapes, audit log; local differential privacy would swamp counts at event scale (a few hundred attendees — assumption). Opt-in only; deleted 30 days after the event.
- **48h prototype:** S — radar panel beside the Need Compiler; switching "Finnish C1" to "B1" changes the band live.
- **Real-world pilot notes:** A sales asset for Business Espoo client managers: "see who is coming before you commit". KPI: companies with published needs at T-7 vs. previous events.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### TECH-11: Synthetic Twin Fairness Dry-Run
- **One-liner:** Before each event the whole pipeline runs on a synthetic population with known attributes, revealing language, career-path and education disparities without collecting sensitive data.
- **Journey stage:** Pre-event, Cross-cutting
- **Primary users:** Organizer, Company
- **Pain points addressed:** P10, P3, P2, P6
- **How it works:** A seeded generator samples ESCO occupation profiles into ~1,000 personas with attributes never collected in production (first language, Finnish level, career changes, Finnish/foreign/no degree, gaps). An LLM writes their stories as parallel texts — the same facts in Finnish, English, Arabic and Ukrainian, "plain" and "AI-polished". The pipeline runs end to end and reports extraction parity (skill recall per language and style against ground truth: a polished twin must not gain claims, an Arabic story must not lose them) and need reachability (which persona groups can fully cover each Need Card, and which requirement is the bottleneck — fed back as TECH-01 lint hints).
- **What makes it new:** Bias testing with parallel synthetic corpora instead of special-category data, which the amended AI Act allows only where strictly necessary ([Council](https://www.consilium.europa.eu/en/press/press-releases/2026/05/07/artificial-intelligence-council-and-parliament-agree-to-simplify-and-streamline-rules/)) — plus a regression gate for every model or prompt change.
- **AI role & human-in-the-loop:** AI generates the data and is the system under test; organisers interpret and act; companies decide on requirement changes.
- **Risks & mitigations (privacy, bias, legal):** Stereotyped personas → attributes assigned by sampling, not by the LLM; templates reviewed by RAI and TAL. Synthetic ≠ real → voluntary, aggregate post-event surveys in a pilot.
- **48h prototype:** S — parity dashboard across four languages and plain/polished twins, plus a Need Card that excludes every foreign-degree persona; it doubles as our demo-data engine (C2).
- **Real-world pilot notes:** Publish the dry-run report with each event; reuse it as technical documentation once Annex III duties apply (December 2027).
- **Self-assessment:** J1 3/5 · J2 4/5 · J3 5/5

## 4. My top 3 features (and why)

1. **TECH-06 Proof Conversations** — the most direct answer to the challenge (J1): structured live interaction is the hardest signal to fake (P6) and the best-evidenced predictor, and it cuts noise (P4). It needs no AI, so Espoo could run it at the next event.
2. **TECH-01 Need Compiler** (with TECH-10 as its test step) — P2 is the upstream root cause; ten minutes of talk beats a form nobody fills in, and the radar rewards doing it early while answering P1.
3. **TECH-04 Rank Needs, Not People** — makes C1, C3 and P8 structurally easier rather than mitigated, and is our most distinctive demo moment (J2, J3): "your data never left your phone".

## 5. Hero concept

**Näyttö — proof, not prose.** Working name: Finnish for "demonstration", the word Finnish vocational education uses for proving competence in real work.

A hiring manager spends ten minutes with the **Need Compiler (TECH-01)**; the **Supply Radar (TECH-10)** shows the City's pool *does* hold matching talent once "native Finnish" becomes "Finnish B1 for customer calls" — P1 and P2 answered on one screen. Talent build an **Evidence-Linked Skill Passport (TECH-02)** by telling stories in their own language. It never leaves their phone, which runs **Rank Needs, Not People (TECH-04)** against the signed catalog and explains every match on a symmetric **Fit Sheet (TECH-05)**. At the event, every meeting is an 8-minute **Proof Conversation (TECH-06)**, and a skill shown live becomes a **Witnessed-Skill Credential (TECH-07)** the talent keeps.

Demo story (three minutes): two synthetic twins of the same woman — one with a ChatGPT-polished CV, one writing plain, non-native English. Same facts, same Fit Sheet, same outcome: polish buys nothing, evidence buys everything. Then she demonstrates a skill on stage, and a juror scans her fresh credential.

## 6. Sources

- [Ars Technica 2025 — LinkedIn/NYT application data](https://arstechnica.com/ai/2025/06/the-resume-is-dying-and-ai-is-holding-the-smoking-gun/)
- [OpenAI 2023 — AI classifier withdrawn](https://openai.com/index/new-ai-classifier-for-indicating-ai-written-text/)
- [Liang et al. 2023 — detector bias, Patterns](https://www.cell.com/patterns/fulltext/S2666-3899%2823%2900130-7)
- [City of Espoo — population 2025](https://www.espoo.fi/fi/kaupunki-ja-paatoksenteko/tutkimus-ja-tilastot/vaesto)
- [City of Espoo 2026 — AI translation experiment](https://www.espoo.fi/en/news/2026/09/espoos-ai-translation-experiment-has-ended)
- [Sackett et al. 2022 — selection validity](https://doi.org/10.1037/apl0000994)
- [ESCO v1.2 launch deck](https://esco.ec.europa.eu/system/files/2024-05/V1.2%20Launch%20-%20ESCO%20SEC%20combined%20-%20final%20clean.pdf)
- [ESCO API](https://esco.ec.europa.eu/en/about-esco/escopedia/escopedia/esco-api)
- [Job Market Finland — how matching works](https://tyomarkkinatori.fi/en/instructions-and-support/personal-customers/instructions-for-the-my-job-path-section/independent-job-search/how-the-matching-works)
- [Job Market Finland — Jobposting API](https://tyomarkkinatori.fi/jobposting-new/documentation/KIPA-manage-jobpostings-en.html)
- [Työmarkkinatori blog — AI-assisted ESCO search](https://tyomarkkinatori.fi/blogit/vieraskyna-niittyla-tekoalyn-hyodyntaminen-esco-osaamisten-haussa)
- [AI Act — Regulation (EU) 2024/1689](https://eur-lex.europa.eu/eli/reg/2024/1689/oj)
- [Council 2026 — Digital Omnibus agreement](https://www.consilium.europa.eu/en/press/press-releases/2026/05/07/artificial-intelligence-council-and-parliament-agree-to-simplify-and-streamline-rules/)
- [Bratby Law 2026 — Regulation (EU) 2026/1744 timetable](https://bratby.law/digital-omnibus-ai-high-risk-delay/)
- [European Commission — prohibited-practices guidelines](https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-01/guide-prohibited_en.pdf)
- [Freshfields 2025 — emotion recognition and candidates](https://www.freshfields.com/en/our-thinking/blogs/technology-quotient/eu-ai-act-unpacked-25-european-commission-releases-critical-ai-act-implementati-102kfql)
- [CJEU C-634/21 SCHUFA](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A62021CJ0634)
- [CJEU C-203/22 Dun & Bradstreet Austria](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX%3A62022CJ0203)
- [W3C 2025 — Verifiable Credentials 2.0](https://www.w3.org/TR/vc-data-model-2.0/)
- [eIDAS 2.0 — Regulation (EU) 2024/1183](https://eur-lex.europa.eu/eli/reg/2024/1183/oj)
- [VirtualBadge — EUDI Wallet timeline](https://www.virtualbadge.io/blog-articles/eidas-2-0-eudi-wallet-what-digital-credentials-must-be-able-to-do-now)
- [AMD Silo AI 2025 — Poro 2](https://www.amd.com/en/blogs/2025/silo-ai-continued-pretraining-provides-blueprint-for-gla.html)
- [EuroLLM 2025 — EuroLLM-22B](https://huggingface.co/blog/eurollm-team/eurollm-22b)
- [Coles et al. 2010 — AEA job-market signalling, JEP](https://www.aeaweb.org/articles?id=10.1257/jep.24.4.187)
