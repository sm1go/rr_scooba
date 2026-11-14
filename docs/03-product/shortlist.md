# Shortlist and MVP decision (after Round 3)

**Status:** recommendation, 14 Nov 2026 ~02:40 — awaiting the owner's OK (D004). Inputs: Round 3 votes
(`docs/02-ideation/round-3-votes/`), the generated ranking (`scoring/final-ranking.csv`), the
catalogue (`feature-catalog.md`).

## Final vote (6 role agents × 100 points)

| Rank | F-ID | Feature | Points | Backers | "Build for real" votes |
|---|---|---|---|---|---|
| 1 | F06 | Sparks — scarce, evidence-paired requests | **141** | 6 | 6 / 6 |
| 2 | F01 | Need Interview → Challenge Card | **117** | 6 | 6 / 6 |
| 3 | F04 | Own-Words Evidence Cards | **89** | 6 | 6 / 6 |
| 4 | F03 | Pool Proof | **81** | 6 | 6 / 6 |
| 5 | F13 | 72-Hour Closure & Next Step | 51 | 6 | 4 / 6 |
| 6 | F10 | Structured Proof Conversations | 42 | 5 | 4 / 6 |
| 7 | F11 | Live Proof Formats | 30 | 6 | 0 / 6 (slide / prop) |
| 8 | F02 | Requirement Reality Check | 27 | 6 | 3 / 6 (others: inside F01) |
| 9 | F18 | Synthetic Twin Fairness Test | 12 | 4 | 1 / 6 (others: real batch, shown as one table) |
| 10 | F14 | Incentives & Permits | 6 | 2 | 0 / 6 (banner inside F13) |
| 11 | F05 | Provenance Ladder | 4 | 1 | 0 / 6 (static chips) |

F07, F08, F09, F12, F15, F16, F17, F19 and F20 received no points.

## Recommended concept — TalentMatch Signal: *proof, not prose*

*Companies bring a problem, talent brings proof, Espoo sets the table.* A signal layer for the City's
TalentMatch events that runs alongside any event platform. Journey: **F01 → F03 → F04 → F06 → F10 → F13**.

**Demo thread (synthetic):** Sanna, founder of a 14-person Espoo software SME, pastes last year's job ad.
The Need Compiler (Nemotron) turns it into a Challenge Card — "our CI pipeline takes 40 minutes", three
must-haves with "how we'll check it" — and flags "fluent Finnish"; Pool Proof shows "fewer than 10",
and "English team, Finnish B1 for customer calls by month 6" brings it back to "20+". Amira, a backend
engineer who moved to Espoo with her spouse, tells two work stories in her strongest language; her card
keeps only claims backed by her own quoted words and refuses an inflated one. She spends one of her
Sparks pairing "cut build time from 30 to 6 minutes" with Sanna's line; Sanna sees evidence pairs, no
names, and accepts — only then does Amira's name appear. On the day, a one-screen Proof Conversation
asks every candidate the same three questions; within 72 hours Sanna closes with two taps and the
desk warns "support may apply — don't sign before the decision". Trust lab: 1,000 synthetic twins
(plain vs AI-polished, different names and languages) produce the same claims.

## MVP cut

**Build for real** — deterministic spine first, AI steps second, each AI step with a recorded fallback:

1. Data model + synthetic seed (two demo personas, ~12 companies, ~300 synthetic talents with stories).
2. F03 Pool Proof bands (k ≥ 10) and F02 lint rules + language grid as tools and card fields.
3. F06 Sparks ledger: budget, pairing claim ↔ card line, reveal on accept, deadline and refund; accept → first free slot (F08-lite).
4. F10 one-screen conversation sheet (three questions from the card, ticks visible to the talent) and F13 two-tap closure with reason chips + F14 banner.
5. F01 Need Compiler agent on **Nemotron 3.5 Super VL** (reads a pasted ad or screenshot; tools: ESCO search, lint, pool bands).
6. F04 story interview + quote-backed extraction + labelled translation on **Gemma**.
7. F18 twin batch on **Modal** → one parity table in a "Trust lab" screen.

**Mock or slide:** F05 static chips · F09 printable QR pass · F11 table-tent prop and pilot slide ·
F15/F16 one organiser tile (zero-meeting list, funnel, "next steps per recruiter-hour") · F17/F19 one trust slide.

**Not now:** on-device matching and the identifiability meter (F07 extras), F08 solver, F12, F20,
credentials, work-sample tasters; never any score, ranking, "fits N of M" or AI-text detection.

## Tech-challenge mapping (D005)

| Challenge | What it powers | Visible demo moment |
|---|---|---|
| Nemotron 3.5 Super VL | F01 agent; F02 and F03 as its tools | Reads a screenshot of last year's ad, flags "fluent Finnish", the pool band drops and recovers |
| Gemma | F04 follow-up questions, quote-backed extraction, labelled translation | An Arabic story becomes an English card with "show original"; an inflated claim is refused |
| Modal | Public demo URL, Whisper for voice, Gemma on GPU, F18 batch | 1,000 twins processed in one fan-out; parity table |
| Codex | Independent reviews and tests during the build | Logged in the repo |

## Design rules adopted in Round 3

- Pool counts only in bands ("fewer than 10", "10–19", "20–49", "50+"); demo numbers are synthetic.
- Spark budget per talent derived from the meeting slots companies declare (at TalentMatch scale
  1,000 talents × 3 Sparks ÷ 40 companies ≈ 75 per company); pairs grouped by card line, two-tap answers.
- A visible company-minutes budget (target ≤ 45 minutes outside the event day); City account
  managers can run the F01 intake.
- Accessibility: tap to pair (no drag), a text option for every voice step, plain language.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Company workload (the scarce side) | City-run intake, two-tap actions, pool proof before any ask, refunds, public reply rates |
| Weaker claims for accented or second-language speakers in F04 | Quote-only claims confirmed by the person; F18 run on exactly this step |
| Small-pool re-identification | k ≥ 10 bands, fixed query shapes |
| Scope vs ~20 build hours | Spine first; checkpoints below; F02/F13 fall back to mocks at 18:00 |
| Prompt injection via talent text | Model output only through schemas; quotes verified server-side |

## Checkpoints (Europe/Helsinki)

- **Sat 09:00** — Espoo mentors: F01, F03, F06 (+ F13) questions; log answers in `docs/01-research/07-espoo-mentor-validation.md`.
- **Sat 12:00** — deterministic walking skeleton end to end; draft submission on the platform.
- **Sat 18:00** — AI steps integrated; otherwise F02/F13 become mocks.
- **Sat 23:00** — feature freeze; then deploy, evals, docs, pitch.
- **Sun 09:30** — final submission (deadline 10:00).
