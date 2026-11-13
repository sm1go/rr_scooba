# 02 — Multi-agent ideation

**Goal:** generate a broad, high-quality list of possible features for the "Rethinking Recruitment"
challenge and select the strongest options through structured, criteria-based peer review.

## The virtual team (one AI agent per role)

| Prefix | Role | Lens |
|---|---|---|
| STR | CEO & Business Strategist | Value proposition per stakeholder, company engagement & trust (P1), incentives, KPIs, pilot & scale path, positioning |
| PM | Head of Product | End-to-end journey, jobs-to-be-done, MVP slicing, success metrics |
| UX | Head of Design & User Research | Personas, emotional journey, interaction & event-format innovation, accessibility, multilingual |
| TECH | CTO & AI/ML Lead | Skills representation (ESCO), explainable matching, robustness to AI-generated content, scalability (P8), privacy engineering |
| RAI | Responsible AI, Privacy & Legal Lead | EU AI Act, GDPR, Finnish law, bias; "trust features" that double as UX |
| TAL | Talent Acquisition & International Recruitment Expert | Recruiter and jobseeker reality, evidence-based selection, international hiring in Finland (P9), public employment services toolbox |

## Rounds

| # | Round | Output | Rule |
|---|---|---|---|
| 1 | Independent ideation | `round-1-proposals/<PREFIX>-*.md` | 8–12 features per role, IDs `<PREFIX>-NN`; nobody sees the others' work |
| 2 | Cross-review | `round-2-reviews/<PREFIX>-review.md` | Each agent scores **every** feature of the other five on J1–J3, clusters duplicates, picks a top 10, flags red flags, recommends a winning concept |
| 3 | Consolidation (facilitator) | `../03-product/feature-catalog.md`, `../03-product/scoring/` | Duplicates merged into `F01…`; scores computed by `scripts/aggregate_scores.py` from **peer scores only** (self-scores excluded) |
| 4 | Final vote | `round-3-votes/<PREFIX>-vote.md` | Each agent allocates 100 points across the catalog (max 25 per feature), chooses a concept, names won't-haves |
| 5 | Shortlist | `../03-product/shortlist.md` | Final ranking + recommended concept, for the team's decision |

## Scoring rubric (integers 1–5)

- **J1 Impact & Relevance (45%)** — 1 = marginal nice-to-have · 3 = clearly solves a stated pain point for one stakeholder group · 5 = solves a core pain point (P1–P6) with measurable value for at least two stakeholder groups.
- **J2 Innovation & UX (35%)** — 1 = common / already exists · 3 = clear improvement on current practice · 5 = genuinely new approach, intuitive, memorable in a demo.
- **J3 Responsible & Feasible (20%)** — 1 = legally/ethically problematic or unrealistic · 3 = feasible with notable risks that need mitigation · 5 = privacy-by-design, human-in-the-loop, technically credible and demoable in 48 h.

**Weighted score** = 0.45·J1 + 0.35·J2 + 0.20·J3 (mirrors the official judging weights).
