# 06 — Prior art: similar solutions on GitHub and in the market

**Why:** know what already exists, so that we (a) do not rebuild commodity parts, (b) reuse good open
components, and (c) can state precisely what is new in our concept (J2). Searched 14 Nov 2026.

## A. Career-fair and event-networking apps (open source)

| Project | What it does | Takeaway |
|---|---|---|
| [EasyHire-CareerFairPlatform](https://github.com/Sushmadeegoju/EasyHire-CareerFairPlatform) | Pre-screening calls a week before the fair; book a slot only if both sides are interested | Mutual-interest booking is known; it is not our differentiator |
| [CareerMatch](https://github.com/wenxuangithub/CareerMatch) (MIT) | Career-fair app: QR codes, digital cards, AI résumé builder **and** GenAI résumé screening | Exactly the "AI writes, AI reads" loop the brief warns about |
| [virtual-career-fair](https://github.com/CPayne6/virtual-career-fair), [WorkPortal](https://github.com/janaadarwish/WorkPortal-Virtual-Career-Fair) | Virtual booths, queues, video calls, recruiter ratings and notes | Booth and queue mechanics are commodity |
| [NetSync](https://github.com/Labi-Joy/NetSync), [event-matcher](https://github.com/kambleakash0/event-matcher), [aiDotEngineer/network](https://github.com/aiDotEngineer/Network), [CorpConnect](https://github.com/AnirudhAP2k/CorpConnect/blob/master/README.md) | AI or vector "compatibility scores" between attendees, pre-event 1:1 requests | Scoring people is the common pattern and our anti-pattern (C1) |
| [Atria](https://github.com/thesubtleties/atria/) (AGPL-3.0) | Open-source event management with networking (Flask, React, Socket.IO) | Possible base for event logistics; AGPL obligations |
| [adamcon](https://github.com/domdomegg/adamcon) (AGPL-3.0) | Minimal 1:1 booking for a small event: fixed 25-minute slots, one meeting point, e-mail only when action is needed, explicit "deliberately not built" list | Design inspiration for a zero-friction event day |

Common pattern: **profile → AI score → booking**. None of them treats AI-generated material as a signal
problem, shows where information came from, or checks fairness, and most rank people.

## B. Skills extraction and ESCO tooling (reusable)

| Project | What it does |
|---|---|
| [esco-skill-extractor](https://github.com/KonstantinosPetrakis/esco-skill-extractor) (MIT, pip) | Embeddings + cosine similarity → ESCO skills and ISCO occupations from job ads or CVs |
| [nestauk/ojd_daps_skills](https://github.com/nestauk/ojd_daps_skills) | Extracts skill phrases from job ads and maps them to ESCO or Lightcast |
| [tabiya-livelihoods-classifier](https://github.com/tabiya-tech/tabiya-livelihoods-classifier/) (MIT code, CC BY 4.0 data) | Entity linking of occupations, skills and qualifications to ESCO |
| [esco-playground](https://github.com/par-tec/esco-playground) | ESCO dataset tooling and NER experiments |
| [jobbot](https://github.com/shruthi-hariprasad/jobbot) | LLM extraction + ESCO normalisation; a verify→revise loop stops the agent from inventing experience |

→ Reuse an existing ESCO mapper instead of building our own.

## C. Conversational skills discovery — closest prior art to our story interview

[Tabiya Compass](https://github.com/tabiya-tech/compass/) is an open-source AI chatbot that interviews
job seekers about their experiences (including informal and unpaid work), maps them to ESCO skills and
links each skill back to what the user said ([docs](https://docs.tabiya.org/our-tech-stack/compass),
[technical overview](https://docs.tabiya.org/our-tech-stack/compass/technical-overview)). It validates
UX-01 and TECH-02. What we must add to be new: a **two-sided** flow (companies' need/problem cards),
**event-bound** use (meetings, not CV generation), **provenance** labels, and human confirmation of every
skill. Check the licence before reusing prompts or code.

## D. Fair and evidence-based hiring

| Tool | What it does | Takeaway |
|---|---|---|
| [Applied](https://appliedhelp.zendesk.com/hc/en-us/articles/360007228333-The-science-behind-sift-questions) (commercial, from the UK Behavioural Insights Team) | Work-sample "sift" questions; answers anonymised, chunked by question, randomised, scored 1–5 by three independent reviewers with a review guide; reviewers also see an "AI answer" reference | Strongest evidence-based precedent; our event-native equivalent is problem cards + evidence pairs + structured conversations |
| [hirekit](https://github.com/venkatmidhunmareedu/hirekit) | Every score cites a verbatim quote or says "no evidence found"; humans make every decision | Use "quote or no claim" in our explanations |
| [clearhire](https://github.com/kyan9400/clearhire) (MIT) | Per-requirement checks with the evidence line, blind by default, refuses protected-trait questions, hash-chained audit log | Evidence per requirement; we go further and do not rank people |
| [Fairhire](https://github.com/hasini-m06/Fairhire) | Bias auditor (disparate-impact ratio) on hiring data | We audit the *system* on synthetic twins, not real people |
| [TalentInfra](https://github.com/Abhilash-0322/zynd-aickathon) | Multi-agent pipeline with W3C credentials whose orchestrator decides ADVANCE / HOLD / REJECT | Precisely the automated decision-making the brief excludes |
| [HyperHire](https://github.com/Dhruv-Sabharwal/HyperHire), [NightSeeker](https://github.com/S-Sigdel/NightSeeker) | Blockchain-based anonymity | Heavy, little value for events |

## E. Credentials for skills witnessed at events

- [Europass European Digital Credentials](https://europass.europa.eu/en/information-developers) — EU
  open-source issuer, viewer and wallet; W3C Verifiable Credentials; European Learning Model.
- [educredentials/ec-issuer](https://github.com/educredentials/ec-issuer) (MIT) — issues Open Badges 3.0 and ELM credentials.
- [Certo](https://github.com/schroedinger-Hat/certo) (AGPL-3.0) — Open Badges 3.0 for workshops and conferences.

→ A "witnessed skill" can be an Open Badges 3.0 / ELM-compatible JSON credential; no blockchain needed.

## F. Real-world formats and context

- [Espoo TalentMatch](https://www.espoo.fi/en/working-life/espoo-talent-hub/talentmatch-recruitment-events):
  200–1000 jobseekers and 5–50 employers per event, in English, online or in person; the platform's
  "smart matching algorithms" are part of the current offer.
- [Tieto × Startup Refugees hackathon](https://www.tieto.com/en/insights/2025/empowering-immigrant-talent-through-a-hackathon/)
  (Espoo, Oct 2025): 22 professionals of immigrant origin solved real business challenges; many said it
  had been a long time since they could show their abilities in a practical setting → supports
  challenge-based event formats (UX-08, STR-08). Tieto is also a Junction 2026 partner.
- [Kiuas AI co-founder matchmaking](https://www.aalto.fi/en/events/kiuas-ai-co-founder-matchmaking-event):
  facilitated two-sided speed dating → structured, facilitated formats work.
- [Espoo's own job-search advice](https://www.espoo.fi/en/articles/top-5-job-search-tips-how-stand-out-stack-applications)
  tells jobseekers to use AI for applications — the City itself accelerates the arms race the challenge describes.

No public repositories from an earlier Espoo recruitment challenge at Junction were found; the
Junction 2025 challenges came from other partners.

## What this means for us

1. Do not compete on "AI match scores" or booking — commodity, and against C1.
2. Differentiate on: needs-first and evidence-first objects on **both** sides; scarcity signals
   instead of persuasive text; provenance instead of AI detection; "why this conversation" with quotes
   and no ranking of people; a fairness dry-run on synthetic twins; an event day that survives peak load.
3. Reuse: an ESCO mapper (esco-skill-extractor or the Tabiya classifier), Compass-style interview
   phases, Open Badges 3.0 for credentials, adamcon-style minimalism.
