# Round 3 vote — TAL (Talent Acquisition & International Recruitment Expert)

## Points allocation
| F-ID | Points | Why (≤ 20 words) |
|---|---|---|
| F06 | 25 | Scarce, evidence-paired interest AI cannot mass-produce; recruiters read evidence pairs, not cover letters, and every talent hears back. |
| F01 | 20 | Fixes late, vague needs upstream; "how will you check it?" changes the evaluation; every later step reuses the card. |
| F03 | 14 | Answers "no suitable candidates" in 30 seconds: "fluent Finnish" 6 → "English team language" 41 makes inclusion self-interest. |
| F04 | 12 | Strongest-language voice intake jobseekers can actually finish; no quote, no claim; supplies the quotes Sparks pair. |
| F10 | 10 | Best-evidenced selection method (structured interviews .42 vs unstructured .19) fitted to a booth slot; pilotable without AI. |
| F13 | 10 | Ends ghosting; warm redirects give people without networks a referral; the next-step desk checks supports before signing. |
| F11 | 4 | Challenge Tables stretch scarce company minutes (~18 people an hour) and show capability live; pilotable on paper. |
| F02 | 3 | Language is the top hiring barrier for internationals; a task × CEFR × "by when" grid makes requirements justifiable. |
| F14 | 2 | Role-level supports and permit pathway at peak intent reframe "free, so low quality" as "the City de-risks your hire". |

## MVP cut (what we build by Sunday 10:00)
- **Build for real** (max 6 F-IDs, in build order): F01 → F03 → F04 → F06 → F10 → F13. Deterministic spine first on synthetic seed data; the two LLM steps (F01 compile, F04 extraction) last, each with a recorded fallback. F01 carries F02's lint rules and language grid as card fields; F13 carries F14's role-level "don't sign before the decision" banner.
- **Clickable mock or slide only:** F11 (Challenge Tables as our pilot proposal), F08 (static agenda from accepted Sparks), F05 (evidence chips as plain labels), F18 (one plain-vs-polished parity number), F15 + F16 (one organiser tile: zero-meeting list, funnel), F12 (a printed badge as stage prop), F09, F17 and F19 (one line each on the architecture and trust slide).
- **Not now:** F07 (names after accept already live in F06), F20, verifiable credentials, on-device matching.

## Tech-challenge fit
- **Nemotron 3.5 Super VL:** F01 Need Compiler agent — reads last year's ad or a screenshot, asks follow-ups, calls F02 lint and F03 count tools; moment: the compiled card flags "fluent Finnish" and the pool count jumps after the rewrite.
- **Modal:** F04 and F18 — public demo URL, Whisper and Gemma served on GPU, the twin batch fanned out; moment: Amira's spoken story becomes quoted claims in seconds.
- **Gemma:** F04 — quote-grounded claim extraction and labelled translation on open weights the City could self-host; moment: an Arabic story becomes an English card with "show original", and "led DevOps" is refused.

## Three ideas for the Espoo mentors at 09:00
- **F01** — Could Business Espoo account managers run a 12-minute Need Interview at T-21 on company visits? When, how and from whom do needs arrive today?
- **F06** — How many requests does a company get vs accept today? Would 3–5 Sparks feel fair to jobseekers, and an answer deadline to companies?
- **F13** — Do companies lose the €5,000 support by signing first? Could the City staff a 72-hour next-step desk for closures, redirects and support checks?

## Biggest risk and mitigation
Company minutes. Every step asks the scarce side for time, and Sparks scale with talent: 1,000 talents × 3 ÷ 40 companies ≈ 75 Sparks each. If that feels heavier than "send an ad, show up", companies walk (P1). Mitigation: size Spark budgets to declared slots, group pairs by card line with two-tap answers, let Business Espoo run intake by phone, show Pool Proof before asking, and count recruiter minutes on screen (target ≤ 60 outside the event day).
