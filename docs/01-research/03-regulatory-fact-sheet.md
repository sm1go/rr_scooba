# Regulatory & ethical fact sheet

The facilitator's fact sheet: dates, provisions and sources. For the in-depth legal analysis and the design patterns to avoid, see the RAI proposal in
[`../02-ideation/round-1-proposals/`](../02-ideation/round-1-proposals/). Relates to C1, C3, C4, C5 and P10.

## 1. EU AI Act (Regulation (EU) 2024/1689) — what applies to us, and when

| Provision | Meaning for a recruitment-event product | Applies from |
|---|---|---|
| Art. 5 prohibitions, incl. **5(1)(f) emotion recognition in the workplace** | Never analyse emotion, "confidence" or "enthusiasm" in video or voice pitches | 2 Feb 2025 |
| Art. 4 AI literacy (amended by the AI Omnibus) | City staff who operate AI tools need AI-literacy support | 2 Feb 2025 |
| **Annex III (4)(a) — high-risk:** AI for recruitment or selection: placing targeted job ads, analysing and filtering applications, evaluating candidates | An AI matcher that ranks or filters candidates is high-risk. It needs risk management, data governance, logging, transparency, human oversight, accuracy and robustness, a conformity assessment and registration | **2 Dec 2027** (moved from 2 Aug 2026 by the AI Omnibus) |
| Art. 6(3) derogation | Narrow procedural or preparatory tasks may fall outside high-risk, **but an Annex III system that profiles natural persons is always high-risk** | With the high-risk rules |
| Art. 26 deployer obligations (the City as deployer) | Human oversight by competent, trained staff; monitoring; log retention; informing affected people | With the high-risk rules |
| Art. 27 fundamental-rights impact assessment (FRIA) | Public-law bodies such as the City must complete a FRIA **before** deploying a high-risk system | With the high-risk rules |
| Art. 50 transparency | Tell people when they are interacting with an AI system (e.g. a chat intake); mark AI-generated content | 2 Aug 2026 (content-marking deadline 2 Dec 2026 for systems already on the market) |
| Art. 3(1) + Recital 12: definition of an "AI system" | Rules defined solely by humans to execute operations automatically are **not** an AI system. A transparent, deterministic matching rule is therefore outside the AI Act, though GDPR still applies | — |

**AI Omnibus status:** political agreement on 7 May 2026, Council final approval on 29 June 2026, formally adopted in autumn 2026. The high-risk Annex III rules now apply from **2 Dec 2027**, the Annex I (product-embedded) rules from 2 Aug 2028. The Art. 5 prohibitions and GPAI obligations are unchanged. [Council timeline](https://www.consilium.europa.eu/en/policies/artificial-intelligence-act/timeline-artificial-intelligence/), [European Commission](https://digital-strategy.ec.europa.eu/en/policies/guidelines-ai-high-risk-systems), [EPRS briefing](https://www.europarl.europa.eu/RegData/etudes/ATAG/2026/789329/EPRS_ATA(2026)789329_EN.pdf), [BSI, Oct 2026](https://www.bsigroup.com/en-GB/insights-and-media/media-centre/press-releases/2026/october/eu-ai-act-ai-omnibus-adopted/)

**Strategic reading:** an Espoo pilot launched in 2027 would fall straight into the high-risk regime. If we design to that standard now, or keep AI out of the evaluative path entirely, we have a credible J3 story and a head start over existing event platforms.

## 2. GDPR

- **Art. 5 principles:** purpose limitation, data minimisation, storage limitation. **Art. 25:** data protection by design and by default.
- **Art. 6 lawful basis:** public task for the City's statutory employment services; consent for optional features. Avoid **Art. 9** special categories (ethnic origin, health). Note that disability or health data can be implied by some subsidy criteria.
- **Art. 22:** the right not to be subject to *solely* automated decisions, including profiling, that have legal or similarly significant effects. Being rejected for a job or a meeting can qualify.
- **CJEU C-634/21 *SCHUFA* (7 Dec 2023):** a score that a third party "draws strongly on" when deciding can itself be an automated decision. A **match score that effectively decides who gets a meeting is risky**. Matching output should inform people who choose; it should not gate access.
- **Art. 35 DPIA:** probably mandatory for a real pilot (new technology, evaluation or scoring, vulnerable data subjects such as jobseekers, larger scale).

## 3. Finnish law

- **Act on the Protection of Privacy in Working Life (759/2004).** §3 necessity requirement: employers may process only data directly necessary for the employment relationship, and this covers applicants. §4: data must be collected primarily from the person. So **no scraping of social profiles**; the candidate is the source.
- **Non-Discrimination Act (1325/2014).** Prohibits discrimination based on age, origin, nationality, **language**, religion, belief, opinion, political activity, trade-union activity, family relationships, state of health, disability, sexual orientation or other personal characteristics. Language requirements must be justified by the actual job.
- **Act on Equality between Women and Men (609/1986)** applies to recruitment as well.
- **Act on Public Employment and Business Services (380/2023).** The legal basis for municipal employment services from 1 Jan 2025, including the City's processing of jobseeker data as a public task.

## 4. Bias evidence to design against

See [02-ai-in-hiring-evidence.md](02-ai-in-hiring-evidence.md): AI-text detectors misclassify non-native writers (61.3 % false positives), and embedding-based résumé ranking shows strong name-based bias.

## 5. Our "compliance-by-design" stance (working hypothesis, to be confirmed in ideation)

1. **AI helps people express themselves.** It structures, translates and asks better questions, and the person confirms every AI output. AI never evaluates a person.
2. **Matching suggestions are transparent, rule-based and explainable.** Both sides see why a suggestion was made. Humans (company, talent, organiser) take every decision, and there are no hard cut-offs.
3. **Identity stays hidden until mutual interest.** No emotion recognition, no AI-text detection, data minimisation and short retention.
4. **Fairness is tested before every event** on synthetic counterfactual profiles, with oversight logs. DPIA and FRIA templates are ready for a real pilot.
