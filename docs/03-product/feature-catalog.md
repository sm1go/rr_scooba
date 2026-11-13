# Consolidated feature catalogue (F01–F20)

Built from the **58 raw ideas** of Round 1 and the duplicate clusters that the Round 2 reviewers proposed
independently (their clusters agreed closely). Every raw idea maps to exactly one F-ID
(`scoring/feature-mapping.csv`). Peer scores per cluster are generated in `scoring/summary.md`
(section "Consolidated features"); they are peer scores only, weighted 0.45·J1 + 0.35·J2 + 0.20·J3.

Stages: **Pre** = before the event, **Day** = event day, **Post** = after, **X** = cross-cutting.
Pain points P1–P10 and constraints C1–C6: `docs/00-challenge/challenge-brief.md`.

## Ranking after Round 2 (peer scores, 6 reviewers)

| Rank | F-ID | Feature | Raw ideas | Mean weighted | Best raw idea | Top-10 mentions | Borda |
|---|---|---|---|---|---|---|---|
| 1 | F06 | Sparks — scarce, evidence-paired requests | 5 | **4.45** | 4.80 | 7 | 64 |
| 2 | F01 | Need Interview → Challenge Card | 5 | **4.31** | 4.65 | 7 | 58 |
| 3 | F11 | Live Proof Formats | 3 | **4.17** | 4.64 | 8 | 35 |
| 4 | F02 | Requirement Reality Check | 3 | **4.09** | 4.16 | 5 | 12 |
| 5 | F04 | Own-Words Evidence Cards | 6 | **4.04** | 4.59 | 6 | 38 |
| 6 | F03 | Pool Proof | 4 | **4.02** | 4.45 | 6 | 36 |
| 7 | F10 | Structured Proof Conversations | 4 | **3.96** | 4.42 | 5 | 37 |
| 8 | F13 | 72-Hour Closure & Next Step | 4 | **3.94** | 4.28 | 8 | 35 |
| 9 | F05 | Provenance Ladder | 1 | **3.88** | 3.88 | 2 | 8 |
| 10 | F12 | No-CV Badges & Printed Story Cards | 1 | **3.82** | 3.82 | 1 | 1 |
| 11 | F08 | Mutual-Yes Scheduler | 2 | **3.79** | 3.93 | 0 | 0 |
| 12 | F14 | Incentives & Permits at the Moment of Intent | 3 | **3.71** | 4.01 | 3 | 3 |
| 13 | F15 | Human Connectors & Second Look | 2 | **3.66** | 3.68 | 0 | 0 |
| 14 | F07 | Identity Last | 2 | **3.64** | 3.97 | 2 | 3 |
| 15 | F19 | Voluntariness Firewall | 1 | **3.64** | 3.64 | 0 | 0 |
| 16 | F18 | Synthetic Twin Fairness Test | 2 | **3.58** | 3.68 | 0 | 0 |
| 17 | F09 | Zero-Login Event Day | 3 | **3.20** | 3.36 | 0 | 0 |
| 18 | F17 | Explain & Contest | 2 | **3.18** | 3.63 | 0 | 0 |
| 19 | F16 | Organiser Intelligence | 2 | **3.07** | 3.31 | 0 | 0 |
| 20 | F20 | Beyond-Employment Lane | 3 | **2.97** | 3.12 | 0 | 0 |

Generated from `scoring/cluster-summary.csv` (mean = mean of member ideas' peer-weighted scores; Borda = 10 points for a reviewer's #1 … 1 for #10).

## Round 2 consensus

- **Concept:** five of six reviewers independently recommended the same journey and four used the same name, *TalentMatch Signal — proof, not prose* (UX: *Common Table*, TAL: *ProofDay*). Core in every recommendation: **F01 → F03 → F04 → F06 → F10 → F13**, with F11 (live tables) in three of six.
- **Cut by (almost) everyone for the build:** on-device matching and credentials (TECH-04, TECH-07), solver-based scheduling (RAI-02, TECH-09 → a greedy mutual-yes scheduler), dashboards (F16 → one funnel tile), F20, any score, ranking or AI-text detection.
- **Biggest risks named:** company workload (the scarce side is asked for intake, answers, tables and closure) → City-run intake, two-tap actions, payoff before ask; bias in voice/story extraction for accented or second-language speakers → run F18 on exactly that component; small-pool re-identification in F03 → k ≥ 10 bands; scope vs ~20 build hours → deterministic spine first, LLM steps with recorded fallbacks; prompt injection through talent text.
- **Changes adopted from the red flags:** F05 shows evidence levels, not authorship ("AI-drafted" chips would track language background); F08 promises no meeting to everyone, only a floor within real capacity among mutual yeses; F13 keeps a sealed minimal outcome record for the discrimination-claim period instead of deleting everything after 30 days (period to verify); F14 shows supports at role level only, never eligibility before selection; event data never links to benefit registers (F19).
- **Gaps raised:** pay range on the card (EU Pay Transparency Directive — to verify), recruiter minutes per event as a metric, no-show handling, export to the company's own ATS, monitoring bias in *human* decisions, assisted and easy-to-read channels, online parity for "witnessed live".

## Company side — before the event

**F01 · Need Interview → Challenge Card** (Pre · PM-01, TAL-01, TECH-01, UX-02, STR-02)
A 3–12-minute voice or chat intake with the hiring manager (or run by a Business Espoo account manager
on the phone) turns a wish list into a one-screen card: the 90-day problem, three must-haves chosen from
ten ("keep three"), and **how each must-have will be checked** in a conversation. "You said / we
compiled" diff, HR approval, export to a job ad. Early cards earn perks (first scheduling access).
P2, P1, P3, P4.

**F02 · Requirement Reality Check** (Pre · RAI-04, TAL-02, UX-03)
A deterministic, non-blocking lint on the card: at most five hints with legal reasons (proxies such as
"native Finnish", degree, nationality, unexplained gaps), each shown with its effect on the pool. A
shared language grid — task × CEFR level × "from when" ("Finnish B1 for customer calls by month 6,
course paid") — used on both sides, plus labelled translation with the original one tap away. P10, P9, P2.

**F03 · Pool Proof** (Pre · STR-01, TECH-10, RAI-05, PM-02)
While writing the card, the company sees banded, k-anonymous counts of opted-in registrants who have
shown each must-have ("20+ with CI/CD evidence"), and how each requirement shrinks or grows the pool —
never an individual (k ≥ 10 bands). Small results read "fewer than 10 — talk to us". Optional consented excerpts and a
"reserve slots" button. P1, P2, P3, P10.

## Talent side — before the event

**F04 · Own-Words Evidence Cards** (Pre · UX-01, RAI-03, PM-03, TECH-02, TAL-04, TECH-03)
A 10-minute voice or chat interview in the person's strongest language (also assisted, e.g. a library
booth) draws out 2–3 concrete work episodes. The AI **asks, never writes**: every claim on the card
quotes the person's own words ("no quote, no claim"), inflated claims are refused, the person confirms
or deletes each line. Transferable-skill bridges (ESCO paths) as prompts. P5, P6, P3, P10.

**F05 · Provenance Ladder** (X · UX-05)
One chip vocabulary on every card, derived from process facts — told → specific → artefact → witnessed
live → introduced by a person (evidence levels, not authorship). Never a score, filter or sort key, and
never an "AI detector"; it never records who used AI. P6, P3, P10.

## Matching and signals

**F06 · Sparks — scarce, evidence-paired requests** (Pre/Day · UX-04, TECH-08, PM-04, STR-04, TAL-05)
Every talent gets 3–5 Sparks; each pairs one of their quotes with one line of a company's card — no
cover letter. Companies review evidence pairs, names appear only after "accept", every Spark must be
answered by a deadline (unanswered ones are refunded), companies have a capped invitation budget,
coarse demand heat shows where competition is, and walk-in time stays reserved. P4, P6, P5, P3.

**F07 · Identity Last** (Pre/Day · RAI-01, TECH-04)
Capability cards stay double-blind until mutual interest; an identifiability meter shows how
recognisable a card is. Option: match needs against cards on the talent's own device so the City never
computes a ranking of people. P10, C3, C1.

**F08 · Mutual-Yes Scheduler** (Pre/Day · PM-05, RAI-02)
Only meetings both sides said yes to are scheduled; a "one before four" floor (everyone gets a first
meeting before anyone gets a fourth, within real capacity), Circles for over-demanded cards, remote
seats, a published tie-break seed and a "why this slot" pop-up. P4, P7, P10.

## Event day

**F09 · Zero-Login Event Day** (Day · PM-07, TECH-09, UX-08)
Agendas are generated before the day as an offline pass (cached web app, QR, SMS and print fallback);
arrival waves, a virtual booth queue and zones replace the doors-open stampede; just-in-time remote rooms. P8, P7.

**F10 · Structured Proof Conversations** (Day/Post · TECH-06, PM-06, TAL-07, RAI-06)
Every booked conversation (7–15 minutes) runs on the card: the same three questions for every
candidate, topics shared ahead (open book), a "show me" minute, one-tap anchored evidence ticks per
must-have that the talent can see; AI may transcribe, never judge; notes purged after 30 days. P6, P4, P3.

**F11 · Live Proof Formats** (Day · UX-07, TAL-06, TECH-07)
Challenge Tables: companies host 20-minute round tables on their problem for rotating small groups
(write first, then talk; remote window seat). Work-sample tasters reviewed code-first, name-last.
"Witnessed live" becomes a chip now; portable credentials later. P6, P3, P4, P9.

**F12 · No-CV Badges & Printed Story Cards** (Day · UX-06)
CVs go to the coat check: each talent wears an "ask me about…" hook and carries printed story cards;
each company wears its problem; QR codes open only what each person chose to share. P5, P6, P4.

## After the event

**F13 · 72-Hour Closure & Next Step** (Post · PM-08, UX-10, TAL-08, STR-06)
Every connection gets an answer within 72 hours: two taps for the company with job-related reason
chips from its own card, an AI-drafted, human-approved message, a warm redirect to a better-fitting
company instead of silence, public reply rates, and content that fades after 30 days unless both keep it
(a sealed minimal outcome record stays for the discrimination-claim period). P1, P5, P10.

**F14 · Incentives & Permits at the Moment of Intent** (Pre/Post · STR-03, TAL-09, TAL-03)
At role level only, the card shows which public supports may apply (e.g. Espoo recruitment support)
and when to act ("don't sign before the decision"); a permit-pathway card and a three-option
right-to-work status appear only after mutual interest; eligibility is checked by an adviser, never
shown before selection. P1, P9.

## Organiser and safety net

**F15 · Human Connectors & Second Look** (Pre/Day · UX-09, PM-09)
Visible City "Connectors" with a list of who still has zero meetings make logged warm introductions on
the floor; a random-order "Second Look" queue lets staff re-check people the flow missed, with a
written rationale. P4, P10, P3, C1.

**F16 · Organiser Intelligence** (X · STR-05, STR-07)
One aggregate, small-cell-suppressed funnel (cards → Sparks → meetings → next steps) and a demand-vs-
supply heatmap that tells the City which events and trainings to run; per-company one-page outcome
report. P1, P2, P3.

## Trust layer

**F17 · Explain & Contest** (X · TECH-05, RAI-09)
A symmetric, score-free "why this conversation" sheet that both sides see identically, including the
smallest change that would alter it; receipts of what the AI did and did not do; a contest button; a
public AI register. C1, C4, C6.

**F18 · Synthetic Twin Fairness Test** (Pre/X · TECH-11, RAI-08)
Before each event the pipeline runs on synthetic twins — the same facts written plainly or AI-polished,
in different languages, with different names or career gaps — and reports flip rates; a release gate
blocks a version that treats twins differently. P10, C5, C2.

**F19 · Voluntariness Firewall** (X · RAI-07)
Event data lives in a separate space and never feeds benefit supervision; only talent-initiated
exports ("count this as a job-search activity") leave it. C3, C4, P5.

## Beyond employment

**F20 · Beyond-Employment Lane** (Pre/Post · STR-08, STR-09, TAL-10)
An "employee or outcome?" fork in the intake: a company can post a problem that becomes a hire, a paid
trial project, a contract with a local micro-firm or a shared part-time role across firms. P2, P1, P5.
