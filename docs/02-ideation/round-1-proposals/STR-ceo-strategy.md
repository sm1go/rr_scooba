# Round 1 Proposal — STR (CEO & Business Strategist)

## 1. Problem analysis from my perspective

**Thesis: Espoo does not have a talent-supply problem. It has a visibility, credibility and incentive-design problem, and AI has just destroyed the last cheap signal of genuine interest.**

1. **P1 is a perception gap, not a supply gap.** In September 2026 the Espoo–Kauniainen employment area had 19,410 unemployed jobseekers (+7.8% y/y), and professionals (*erityisasiantuntijat*) were the largest occupational group among them ([Espoo, 9.11.2026](https://www.espoo.fi/fi/uutiset/2026/11/tyollisyys-ja-kotoutumisjaosto-kasitteli-tyollisyyden-tilannekuvaa-9112026); [subcommittee papers](https://espoo.oncloudos.com/kokous/20261754.PDF)). In March 2026, 6,780 unemployed held a higher-education degree and 42.3% were foreign-language speakers, a group in which higher education is prominent ([situation report](https://espoo-sv.oncloudos.com/kokous/20261673-3-354122.PDF)). Yet just under half of Finnish SMEs say a lack of skilled labour restricts their growth ([SME Barometer 2026](https://www.yrittajat.fi/ajankohtaista/tutkimukset/pk-yritysbarometri-1-2026/)). Shortage and surplus coexist, which is a matching failure. When Employment Services visited companies in 2025, employers were "delighted by how many talents are available" ([Espoo](https://www.espoo.fi/en/news/2025/10/free-recruitment-help-sparks-interest-entrepreneurs-espoo-are-delighted-about-level-talent)). Perception flips on contact, but a few specialists cannot visit every SME. **The product has to scale that surprise.**

2. **Demand is invisible until it is too late (P2).** Only 796 vacancies were registered with Espoo's employment services against 19,014 unemployed residents ([Espoo statistics](https://www.espoo.fi/fi/kaupunki-ja-paatoksenteko/tutkimus-ja-tilastot/tyossakaynti-tyopaikat-ja-tyottomyys)), and company visits surfaced "hidden jobs". Submitting late is rational: a precise, early need costs effort and earns nothing extra. Late needs are an incentive problem, not a form problem.

3. **"Free" reads as "low quality" because there is no price to signal quality.** The City has to replace price with signals private platforms cannot copy (selectivity, verification, accountability, outcomes) and with money. Only the City can attach euros to a match: its own €5,000 recruitment support for hiring an unemployed resident under 30 or a foreign-language speaker (€1.5M ≈ 300 hires in 2026, granted *before* employment starts), plus pay subsidy, RekryKoulutus and a free tailored candidate search ([supports](https://www.espoo.fi/fi/rekrytointituet); [recruitment support](https://www.espoo.fi/fi/rekrytointituki); [candidate search](https://www.espoo.fi/en/news/2026/05/how-your-business-doing-invite-us-visit)). None of this appears in today's event journey.

4. **The City has financial skin in the game.** Since 2025 municipalities pay 10–50% of unemployment benefits from day 101 ([Kela](https://www.kela.fi/samarbetspartner-kommuner-finansiering-av-arbetsmarknadsstodet)). The municipal bill was heading for €750–800M in 2025, €50–100M over forecast ([Kuntaliitto](https://www.kuntaliitto.fi/blogi/2025/tyottomyyden-kustannukset-karkaavat-kasista)), and 41.7% of Espoo's unemployed are long-term unemployed. Better matchmaking is a budget line, which is how a pilot gets funded.

5. **AI made applications free, so they stopped carrying information (P6).** LinkedIn handles about 11,000 applications per minute, up 45% in a year ([Ars Technica on NYT data](https://arstechnica.com/ai/2025/06/the-resume-is-dying-and-ai-is-holding-the-smoking-gun/)). A signal that costs nothing tells you nothing, and employer-side AI screening only escalates the arms race. The signals that stay informative are **scarce** (you can send only a few) or **observed** (a human saw you do it).

6. **What incumbents get wrong.** Brella, Swapcard, b2match and Tavata sell event logistics plus "AI matchmaking" on self-declared interests, and they optimise for meeting *volume*; Swapcard auto-releases slots "to maximize meeting volume" ([Swapcard](https://www.swapcard.com/features/event-networking); [Brella](https://www.brella.io/event-matchmaking); [Tavata](https://tavata.events/en/solutions/recruiting-events)). Job boards (LinkedIn, Duunitori, The Hub) are post-and-pray and flooded with AI applications, and Job Market Finland has profiles but no event moment ([Business Espoo](https://www.espoo.fi/en/business-espoo-helping-companies-thrive/services-supporting-business-growth/recruitment-assistance)). None of them measures hires, brings public incentives into the match, or is neutral. Espoo's Deep Tech Talent Forum already hand-picks who gets matchmaking access ([Espoo](https://www.espoo.fi/en/DeepTechTalentForum)). The instinct is right, but manual curation does not scale and is where bias and C1 risks sit. **Positioning: the City's neutral trust, signal and incentive layer on top of whatever event platform is procured.**

7. **Regulatory timing rewards designing out of high risk.** Recruitment AI is high-risk under AI Act Annex III from 2 December 2027 ([Council](https://www.consilium.europa.eu/en/policies/artificial-intelligence-act/timeline-artificial-intelligence/)). My rule: **AI works on the company side (needs, demand); mechanisms and humans work on the people side.**

## 2. Opportunity areas ("How might we…")

- HMW make the City's talent pool visible and credible to a sceptical company in under two minutes, without exposing a single individual? (P1, P3, P10)
- HMW make submitting a specific need three weeks before the event the obviously better deal for a busy SME founder? (P2, P1)
- HMW turn "free" into "free, curated and financially de-risked" with incentives only the City can offer, without stigmatising the people those incentives target? (P1, P9, P10)
- HMW restore a costly but fair signal of genuine interest when AI makes applications free? (P4, P6, P7)
- HMW prove in hires and euros, to companies and to the City council, that an Espoo event beats a paid channel? (P1, P3)
- HMW make an Espoo pilot the default kit for Helsinki, Vantaa and the other Talent Boost cities? (P1, P5, P9)

## 3. Feature ideas

### STR-01: Pool Proof — live, anonymous talent-supply counter with requirement elasticity
- **One-liner:** A company describes its need and sees at once how many opted-in people in the City's pool match it, and how each requirement changes that number. It never sees an individual.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P1, P2, P3, P10
- **How it works:** An account manager sends a link: "See who's in the pool for your role." The company types or dictates its need, which is mapped to editable ESCO skills, and a live counter shows matches by evidence level (self-declared, demonstrated at an event, advisor-verified). Each requirement is a must/nice/trainable chip that updates the count (synthetic demo: "fluent Finnish" gives 6, "English working language" gives 41). Proxies such as degree titles get a skills-based alternative. One click turns the result into a Need Card for TalentMatch.
- **What makes it new:** It replaces "please come to our free event" with evidence of supply at the moment of decision, and de-biasing becomes self-interest rather than a lecture. Event platforms show attendees only after you join, and Job Market Finland exposes individual profiles.
- **AI role & human-in-the-loop:** An LLM suggests ESCO skills from the company's text, and the company edits every chip. Counting is a deterministic query over structured skills that talent opted in to share, so nobody is scored, ranked or shown.
- **Risks & mitigations (privacy, bias, legal):** Cells below k = 10 show "fewer than 10", counts are rounded to 5, and queries are limited to 4 filters, rate-limited and logged. There are no filters on nationality, age, gender, permit status or proxies for them, and language appears only as job-relevant proficiency. Only revocable opt-in profiles are counted.
- **48h prototype:** S — the need input feeds a live elasticity counter over 2,000 synthetic ESCO-coded profiles, and the k-threshold visibly kicks in.
- **Real-world pilot notes:** Run with Business Espoo account managers before one TalentMatch. The pool is consenting registrants plus Espoo Talent Hub clients (legal basis to be confirmed by the DPO). KPIs: share of viewers who register, share of needs that drop hard Finnish requirements, pool size per need.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### STR-02: Commitment Ladder — commit early, get curated
- **One-liner:** A transparent tiered deal: the earlier and more specific a company's Need Card, the more the City gives back.
- **Journey stage:** Pre-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P2, P1, P4, P8
- **How it works:** The event page shows three rungs with deadlines. **Gold** requires a complete Need Card and the Fair Recruiter Pledge (STR-06) by T-21. It earns an advisor-curated list of mutually interested talent at T-7, an early start of the free employment-services candidate search, priority slots and an incentive pre-check. **Silver** (by T-14) publishes the need and shows token requests early. **Bronze** gets a table and walk-up conversations. A Need Card takes 10 minutes as a voice note or a call: AI drafts it and the company approves. Because meetings are pre-scheduled, platform load is also spread away from the opening minute (P8).
- **What makes it new:** It is early-bird pricing without a price. The currency is the City's scarce human capacity (curation, candidate search, advisor time), given to early committers, which also lets the City plan its workload. No private platform can offer a public candidate search as the reward.
- **AI role & human-in-the-loop:** AI structures the company's own need and the company approves it. An advisor reviews Gold cards before curating. AI makes no decisions about people.
- **Risks & mitigations (privacy, bias, legal):** Firms without HR teams could lose out, so an advisor-assisted intake counts as Gold. There are no paid tiers, the rules are published and Gold capacity is capped per event.
- **48h prototype:** S — an event page with the ladder and a countdown, a 90-second voice-to-Need-Card flow and the organiser board.
- **Real-world pilot notes:** Today needs arrive "just before the event day"; the target is at least 60% of complete Need Cards by T-14. Employment services reserve candidate-search capacity for each event.
- **Self-assessment:** J1 5/5 · J2 3/5 · J3 5/5

### STR-03: Incentive Stack — the free service that pays you back (with a privacy firewall)
- **One-liner:** Every Need Card shows, at role level, which public supports and services could apply and when to act. Whether an individual is eligible stays invisible until both sides opt in.
- **Journey stage:** Pre-event, Post-event
- **Primary users:** Company, Organizer
- **Pain points addressed:** P1, P9, P10, P2
- **How it works:** Four role-level questions (contract ≥12 months? ≥80% working time? sector? location?) produce a stack: Espoo recruitment support (€5,000), the youth voucher, pay subsidy, 55+ support, RekryKoulutus, the free candidate search and Omnia apprenticeships. For international hires it adds Espoo Talent Hub, the Work in Finland [Talent Manager Network](https://www.workinfinland.com/en/tyonantajat/palvelut/talent-manager-network/) and the Finnish Immigration Service's employer services. Timing alerts protect the company, e.g. "Espoo recruitment support must be granted before employment starts, so book the advisor call before sending the offer." After a mutual match the candidate can tap "ask my employment-services advisor about support", and the advisor confirms eligibility.
- **What makes it new:** This is the moat: no private platform can attach public money and services to a match. The firewall is based on evidence. In the Dayton experiment, jobseekers whose vouchers announced their subsidy eligibility were *less* likely to be hired ([Burtless 1985](https://doi.org/10.1177/001979398503900108)), while subsidies bundled with job development did better ([Katz 1996](https://ideas.repec.org/p/nbr/nberwo/5679.html)).
- **AI role & human-in-the-loop:** A rules engine, not AI, builds the stack. An optional LLM answers only from City-approved pages, with citations. A City official always decides eligibility and grants.
- **Risks & mitigations (privacy, bias, legal):** Age and language are protected grounds, so eligibility attributes never appear in discovery or ordering. Rules change (Espoo-lisä was [paused in June 2025](https://www.espoo.fi/fi/uutiset/2025/06/espoo-ei-myonna-uusia-tyollistamisen-espoo-lisia-loppuvuonna-2025-maararaha-kohdennetaan) and the new support opened on 3 Feb 2026), so employer services own the content and show "last verified" dates. Results read "may apply, not a decision", and caps are shown.
- **48h prototype:** S — a rules engine with 7 schemes, a € range for each synthetic role, the timing alert and the consent tap.
- **Real-world pilot notes:** KPIs: share of the roughly 300 supported hires that start at events, and time from match to support decision. Employment Services govern the content.
- **Self-assessment:** J1 5/5 · J2 4/5 · J3 4/5

### STR-04: Signal Tokens — scarce, equal "I really mean it" tickets
- **One-liner:** Every participant gets a few equal tokens that cannot be bought (e.g. talent 3, companies 5) to attach to meeting requests. They bring back the costly signal of genuine interest that AI mass applications destroyed.
- **Journey stage:** Pre-event, During event
- **Primary users:** Talent, Company, Organizer
- **Pain points addressed:** P4, P6, P3, P7
- **How it works:** Talent browse Need and Challenge cards, and companies browse anonymised capability cards. Ordinary requests are capped (e.g. 10). Token requests go to the top of the recipient's inbox, and the scheduler books mutual-token pairs first. A coarse "demand heat" indicator (low/medium/high) nudges talent to spread tokens beyond three famous brands, and unused tokens expire. Companies see messages like "14 people spent a token on your need", a demand signal that keeps them engaged (P1).
- **What makes it new:** It is proven market design, new to public recruitment events. The economics job market has used preference signals since 2006 ([Niederle](https://web.stanford.edu/~niederle/)), and in a field experiment attaching a "virtual rose" substantially raised acceptance without crowding out other offers ([Lee & Niederle 2015](https://link.springer.com/article/10.1007/s10683-014-9425-9)). It is AI-proof by construction: an LLM can write a thousand applications but cannot create a fourth token. One decision also replaces filter-heavy matching screens (P7).
- **AI role & human-in-the-loop:** No AI. It is a pure mechanism, and every choice is made by a human.
- **Risks & mitigations (privacy, bias, legal):** Many rose-study participants misused their roses, so coaches plan token use with jobseekers and an on-site Matchmaker Desk of City advisors makes warm introductions for people without meetings. Coarse heat instead of exact counts prevents herding. Everyone gets the same number of tokens, none are paid for or given as bonuses, and tokens received are not used for ranking. The only data stored is a counter.
- **48h prototype:** S — a token wallet, requests with or without a token, inbox ordering, a mutual-token scheduler and live metrics.
- **Real-world pilot notes:** A/B test in one online [TalentMatch](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events) (200–1,000 jobseekers, 5–50 employers). Compare acceptance of token vs. non-token requests, meeting relevance and company time per relevant meeting.
- **Self-assessment:** J1 4/5 · J2 5/5 · J3 5/5

### STR-05: Impact Ledger — proof of value for companies, public value for the City
- **One-liner:** Consent-based tracking from meeting to interview, hire or contract and 6-month retention. It produces a one-page ROI report for each company and a public-value dashboard for the City.
- **Journey stage:** Post-event, Cross-cutting
- **Primary users:** Company, Organizer
- **Pain points addressed:** P1, P3, P10
- **How it works:** Companies update each meeting in two clicks or answer three-question pulses at T+14, T+45 and T+180, and talent confirm the outcome independently. Each company gets a report such as "9 meetings, 3 interviews, 1 hire, 3.5 hours invested, €5,000 support used". The City dashboard tracks need lead time, conversion, returning companies, incentive uptake, feedback coverage and outcome parity across language groups (aggregated, small cells suppressed). It also shows estimated savings: Σ (benefit days avoided × daily benefit × municipal share of 10–50%). *Illustrative assumption:* if a long-term unemployed person (40% share, ~€37/day) is hired three months earlier, the City saves about €960 in benefit share before tax effects.
- **What makes it new:** Event platforms report engagement; this reports hires and euros. Each company report becomes sales material for the next event, which closes the P1 loop, and the council gets evidence instead of anecdotes.
- **AI role & human-in-the-loop:** No AI on outcomes. An optional LLM writes a narrative over aggregates only.
- **Risks & mitigations (privacy, bias, legal):** The ledger uses pseudonymous IDs, consent and 12-month retention, and only aggregates leave the system. Fairness monitoring uses only language data the City already holds lawfully as the employment authority, and never for matching. Both sides report outcomes to limit gaming, and the pilot cross-checks against the employment-services register (with DPO approval).
- **48h prototype:** M — synthetic outcomes, a generated company PDF and City dashboard tiles with suppression applied.
- **Real-world pilot notes:** Baseline from the last three TalentMatch events, with a quarterly report to the employment and integration subcommittee. The City runs the savings model on its own Kela invoice data.
- **Self-assessment:** J1 4/5 · J2 3/5 · J3 4/5

### STR-06: Fair Recruiter Pledge — accountability as the City's currency
- **One-liner:** Companies earn a public "Espoo Fair Recruiter" mark by committing to, and being measured on, five practices: a real and budgeted role, a reply to every token request within 5 working days, one-click feedback after every meeting, realistic language requirements and a decision-maker at the table.
- **Journey stage:** Cross-cutting
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P1, P4, P5, P10
- **How it works:** Companies take the pledge as part of Gold sign-up, and it is measured automatically (reply rate, median reply time, feedback coverage). Talent see the badge and these three numbers on every company card. Feedback is structured as "strength we saw / gap to work on / next step", which gives talent words for their own value (P5). Companies that keep the pledge are featured in Business Espoo channels, in HeRoHub (Espoo's HR community) and on a yearly list, while those that break it quietly lose Gold priority.
- **What makes it new:** Platforms rate individual meetings (Brella's 1:1 ratings are in beta). Here the public organiser turns its convening power and channels into employer-branding value and tackles ghosting, which erodes talent trust in events. The "real role" commitment also counters ghost postings.
- **AI role & human-in-the-loop:** The metrics need no AI. An optional assistant drafts kind, specific feedback from a recruiter's bullet points, which the recruiter edits and sends.
- **Risks & mitigations (privacy, bias, legal):** The burden stays light: five commitments, one-click feedback and positive framing. Only positive marks are public, metrics are company-level rather than per recruiter, and structured fields keep discriminatory remarks out of feedback.
- **48h prototype:** S — a badge with three live numbers, the one-click feedback form and a pledge-breach state.
- **Real-world pilot notes:** Co-design the commitments with HeRoHub and Espoon Yrittäjät. KPIs: feedback coverage, talent NPS, returning companies.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 5/5

### STR-07: Demand Radar — events as a year-round demand-sensing pipeline
- **One-liner:** Need Cards, Pool Proof queries and token flows feed a demand-vs-supply heatmap that tells the City, months ahead, which events to run, which RekryKoulutus to commission and which skills to coach.
- **Journey stage:** Cross-cutting
- **Primary users:** Organizer, Company
- **Pain points addressed:** P2, P3, P5, P1
- **How it works:** The radar clusters needs by ESCO skill group, sector and hiring window and overlays the supply of consenting talent. It offers three actions. **Gap** (demand without supply) drafts a RekryKoulutus proposal with Omnia or another provider, where the employer pays 30% ([suomi.fi](https://www.suomi.fi/palvelut/rekrykoulutus-keski-pohjanmaan-tyollisyysalue/07722e0b-46f1-4653-8e52-45113bc48949)). **Hidden surplus** (supply without demand) gives account managers sectors to approach, e.g. "43 people with demonstrated test-automation skills: invite manufacturing SMEs". **Timing** proposes themes and dates for the next events. Coaches also get a monthly "skills in demand" brief to help jobseekers translate their transferable skills (P5).
- **What makes it new:** Events stop being one-off campaigns and become the City's earliest local demand signal, filling the gap between long-range skills anticipation and vacancies already posted.
- **AI role & human-in-the-loop:** AI clusters and summarises company needs, with no personal data involved. Human planners decide.
- **Risks & mitigations (privacy, bias, legal):** Hiring plans are commercially sensitive, so companies opt in, data is aggregated across at least 3 companies and shared views carry no names. Supply counts use the same k-anonymity rules as STR-01.
- **48h prototype:** M — a heatmap over synthetic needs and supply with a "Gap → RekryKoulutus draft" button.
- **Real-world pilot notes:** Use it for Espoo Talent Hub's quarterly event planning. KPIs: share of events themed from radar data, RekryKoulutus fill rate and hire rate.
- **Self-assessment:** J1 4/5 · J2 3/5 · J3 5/5

### STR-08: Challenge Market — post a problem, not a job title (hire, contract or partner)
- **One-liner:** Companies post a concrete business problem instead of a job title. Talent, freelancers and micro-firms answer with a 150-word approach or a 3-minute pitch, and a good answer can become a hire, a paid trial project or a supplier contract.
- **Journey stage:** Pre-event, During event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P2, P5, P6, P1
- **How it works:** The intake asks "what problem must be solved in the next six months?" and adds success criteria. Talent choose up to three challenges and submit a short approach, which a company reviewer first reads with name and CV hidden. The strongest approaches get pitch slots, which TalentMatch already offers. Each conversation ends in one of three tracks: employment (with STR-03), a paid trial or freelance project (with Business Espoo's free start-up advice), or a B2B partnership, which covers the "service needs" side of the brief.
- **What makes it new:** SMEs know their problem, not the job title, and a polished CV cannot defend an approach in a live conversation. Because Business Espoo combines employment and entrepreneur services, hiring, contracting and partnering become one flow.
- **AI role & human-in-the-loop:** AI helps phrase challenges and provides translation. Approaches are never scored by AI; humans read them.
- **Risks & mitigations (privacy, bias, legal):** To prevent unpaid spec work, approaches are capped at 150 words or 3 minutes, with no deliverables and no use of ideas without a contract. The anonymised first read reduces bias, and AI-assisted drafts are fine because depth is tested live.
- **48h prototype:** M — a challenge card, approach submission, an anonymised reviewer view and a three-track outcome selector.
- **Real-world pilot notes:** Run one TalentMatch track (e.g. deep-tech SMEs) challenge-first and compare relevance and satisfaction with a job-title track.
- **Self-assessment:** J1 4/5 · J2 4/5 · J3 4/5

### STR-09: Shared Hire — pooling fractional SME needs into real jobs
- **One-liner:** The platform spots complementary part-time needs across Need Cards (e.g. three firms that each need two days a week of export sales to Germany) and offers them as one shared role. This creates jobs no micro-company would post alone.
- **Journey stage:** Pre-event, Post-event
- **Primary users:** Company, Talent, Organizer
- **Pain points addressed:** P2, P1, P5
- **How it works:** Need Cards ask "how much of this do you really need?" (days per week, duration). The organiser sees suggested bundles (same skill cluster, compatible days, no direct competitors) and offers them to the firms. An accepted bundle becomes one Shared Hire card, and talent meet all the partner firms in a single slot. A contract pack explains the options: several part-time contracts, one lead employer with service agreements to the others, or freelancing with Business Espoo support.
- **What makes it new:** Hidden demand in micro-firms is fractional, while job boards and event platforms handle only whole jobs. Turning three "maybe later" needs into one real job is a new kind of match.
- **AI role & human-in-the-loop:** AI suggests bundles from company-side data. The organiser and the firms decide, and nobody is profiled.
- **Risks & mitigations (privacy, bias, legal):** City legal and the social partners review the templates (labour law, collective agreements) before the pilot, and talent get one contact person and protected total hours. Incentives are flagged honestly: [pay subsidy](https://www.espoo.fi/fi/palvelut/palkkatuki-tyonantajalle) covers part-time work, but the €5,000 support requires at least 80% working time. To respect competition law there are no wage-fixing or no-poach clauses.
- **48h prototype:** S — bundle suggestions from synthetic fractional needs, a Shared Hire card and a contract-options explainer.
- **Real-world pilot notes:** Start with 3–5 bundles in one sector through Espoon Yrittäjät. KPIs: bundles formed, hires and 6-month retention.
- **Self-assessment:** J1 3/5 · J2 5/5 · J3 3/5

## 4. My top 3 features (and why)

1. **STR-01 Pool Proof** answers P1 at the moment of decision with evidence instead of persuasion. It doubles as de-biasing (P10) and exposes nobody. It is the most persuasive 30 seconds we can show officials who hear "you have no suitable candidates" every week.
2. **STR-04 Signal Tokens** is the sharpest answer to the challenge's question about AI, because scarcity cannot be generated. It is proven market design, uses no personal data and no AI, can be built in hours and is memorable on stage ("everyone gets three golden tickets").
3. **STR-03 Incentive Stack** is the moat. LinkedIn, Brella and Duunitori can never attach €5,000, a candidate search or co-funded training to a match, and the evidence-based firewall keeps it fair.

STR-02 and STR-05 hold the rest together: the ladder fixes P2, and the ledger proves value and justifies funding the pilot.

**Path to scale:**
1. A 48h demo.
2. One TalentMatch pilot in 2027, bought as a small procurement under the €60k national threshold ([hankinnat.fi](https://www.hankinnat.fi/mika-julkinen-hankinta/kynnysarvot)).
3. Helsinki and Vantaa, which already share one [employer helpline](https://www.espoo.fi/en/business-espoo-helping-companies-thrive/contacts-employers-and-businesses) with Espoo.
4. The [Talent Boost](https://tem.fi/en/talent-boost-en) network, through an open-source (EUPL) City Kit.

Because the 2026 procurement reform restricts in-house routes ([Valtioneuvosto](https://valtioneuvosto.fi/-/1410877/uusi-hankintalaki-voimaan-lisaa-kilpailua-julkisiin-hankintoihin)), open source with competing providers is the realistic multi-city model. No step needs a high-risk AI conformity assessment before December 2027.

## 5. Hero concept

**TalentMatch Signal** is a trust-and-incentive layer for the City's existing TalentMatch events, running alongside whatever event platform is procured.

Demo story (synthetic data):
1. A Business Espoo account manager sends a link to the founder of a 30-person photonics SME. In **Pool Proof (STR-01)** she dictates "someone to automate our optical test bench" and sees 41 people. Ticking "fluent Finnish" drops the count to 6, so she switches to "English working language".
2. The **Incentive Stack (STR-03)** shows that the role may qualify for the €5,000 Espoo recruitment support, with the warning "apply before the contract starts".
3. Through the **Commitment Ladder (STR-02)** she submits her Need Card at T-21 and reaches Gold.
4. Amira, a test engineer who has been looking for work for eight months, spends one of her three **Signal Tokens (STR-04)** on the role. The company spends one of its five on her anonymised capability card, and the mutual-token meeting books itself.
5. After the event the **Impact Ledger (STR-05)** sends the company a one-page report (11 token requests, 4 meetings, 2 interviews, 1 hire) and shows the City conversion, incentive uptake and estimated benefit-share savings.

That report is what Business Espoo sends to the next hundred companies.

Pitch line: *"Free stops meaning cheap when it comes with proof, priority and money, and when interest has to be spent rather than generated."*

## 6. Sources

- Espoo labour market: [subcommittee 9.11.2026](https://www.espoo.fi/fi/uutiset/2026/11/tyollisyys-ja-kotoutumisjaosto-kasitteli-tyollisyyden-tilannekuvaa-9112026) · [meeting papers](https://espoo.oncloudos.com/kokous/20261754.PDF) · [situation report (March 2026)](https://espoo-sv.oncloudos.com/kokous/20261673-3-354122.PDF) · [statistics](https://www.espoo.fi/fi/kaupunki-ja-paatoksenteko/tutkimus-ja-tilastot/tyossakaynti-tyopaikat-ja-tyottomyys)
- [SME Barometer 1/2026](https://www.yrittajat.fi/ajankohtaista/tutkimukset/pk-yritysbarometri-1-2026/)
- Espoo employer services: [company visits (2025)](https://www.espoo.fi/en/news/2025/10/free-recruitment-help-sparks-interest-entrepreneurs-espoo-are-delighted-about-level-talent) · [candidate search (2026)](https://www.espoo.fi/en/news/2026/05/how-your-business-doing-invite-us-visit) · [recruitment assistance](https://www.espoo.fi/en/business-espoo-helping-companies-thrive/services-supporting-business-growth/recruitment-assistance) · [employer contacts](https://www.espoo.fi/en/business-espoo-helping-companies-thrive/contacts-employers-and-businesses)
- Incentives: [Espoo supports](https://www.espoo.fi/fi/rekrytointituet) · [€5,000 support](https://www.espoo.fi/fi/rekrytointituki) · [2026 decision](https://www.espoo.fi/fi/uutiset/2025/12/kaupunginhallitus-espooseen-uusi-rekrytointituki-vuodelle-2026) · [Espoo-lisä paused](https://www.espoo.fi/fi/uutiset/2025/06/espoo-ei-myonna-uusia-tyollistamisen-espoo-lisia-loppuvuonna-2025-maararaha-kohdennetaan) · [pay subsidy](https://www.espoo.fi/fi/palvelut/palkkatuki-tyonantajalle) · [RekryKoulutus](https://www.suomi.fi/palvelut/rekrykoulutus-keski-pohjanmaan-tyollisyysalue/07722e0b-46f1-4653-8e52-45113bc48949)
- Benefit financing: [Kela](https://www.kela.fi/samarbetspartner-kommuner-finansiering-av-arbetsmarknadsstodet) · [Kuntaliitto](https://www.kuntaliitto.fi/blogi/2025/tyottomyyden-kustannukset-karkaavat-kasista)
- Talent services: [Espoo Talent Hub](https://www.espoo.fi/en/working-life/espoo-talent-hub) · [TalentMatch](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events) · [Deep Tech Talent Forum](https://www.espoo.fi/en/DeepTechTalentForum) · [Talent Manager Network](https://www.workinfinland.com/en/tyonantajat/palvelut/talent-manager-network/) · [Talent Boost](https://tem.fi/en/talent-boost-en)
- AI applications: [Ars Technica (NYT data)](https://arstechnica.com/ai/2025/06/the-resume-is-dying-and-ai-is-holding-the-smoking-gun/)
- Competitors: [Swapcard](https://www.swapcard.com/features/event-networking) · [Brella](https://www.brella.io/event-matchmaking) · [Brella features](https://www.brella.io/what-you-get) · [b2match](https://www.b2match.com/value-adds/event-matchmaking) · [Tavata](https://tavata.events/en/solutions/recruiting-events)
- Regulation and procurement: [AI Act timeline](https://www.consilium.europa.eu/en/policies/artificial-intelligence-act/timeline-artificial-intelligence/) · [thresholds](https://www.hankinnat.fi/mika-julkinen-hankinta/kynnysarvot) · [procurement reform 2026](https://valtioneuvosto.fi/-/1410877/uusi-hankintalaki-voimaan-lisaa-kilpailua-julkisiin-hankintoihin)
- Research: [Lee & Niederle 2015](https://link.springer.com/article/10.1007/s10683-014-9425-9) · [Niederle (AEA signalling)](https://web.stanford.edu/~niederle/) · [Burtless 1985](https://doi.org/10.1177/001979398503900108) · [Katz 1996](https://ideas.repec.org/p/nbr/nberwo/5679.html)
