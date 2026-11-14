# Round 3 vote — PM (Head of Product)

## Points allocation
| F-ID | Points | Why (≤ 20 words) |
|---|---|---|
| F06 | 22 | North star in one gesture: quote-paired, scarce requests replace cover letters; 14 evidence pairs, not 140 messages. No AI. |
| F01 | 20 | Fixes late, vague needs (P2); every later step points at card lines. Pilotable next month inside account-manager visits. |
| F04 | 16 | Answers P5/P6: AI asks, never writes; no quote, no claim. Refusing an inflated claim is a demo highlight. |
| F03 | 15 | Refutes "no suitable candidates" (P1) at decision time; banded counts reward dropping proxies. Payoff before any company ask. |
| F10 | 9 | Upgrades the event's core product: same three questions, a show-me minute, evidence ticks the talent sees. No AI judging. |
| F13 | 9 | Ends ghosting: two-tap answers and warm redirects within 72 hours; yields the outcome data that proves value (P1). |
| F11 | 5 | Honest answer to slot math: one Challenge Table host meets 18 people an hour. Pitch as a pilot format. |
| F02 | 2 | Powers the demo hinge: "fluent Finnish" becomes "Finnish B1 by month 6", with a legal reason. Deterministic rules. |
| F18 | 2 | J3 proof on our only people-side AI: plain, polished and second-language versions of one story; show flip rates. |

## MVP cut (what we build by Sunday 10:00)
- **Build for real** (max 6 F-IDs, in build order): **F01 → F04 → F03 → F06 → F10 → F13** — card types first, then the deterministic mechanics that read them. One happy path each on seeded synthetic data (two personas, 300 cards from the F18 twin generator); skeleton through all six by Saturday noon, then F01/F04 LLM steps with recorded fallbacks; freeze Saturday 23:00.
- **Clickable mock or slide only:** F02 (lint hint and CEFR picker inside the F01 card), F05 (evidence chips), F08 (accept → first free slot), F11 (overflow Table seat, format slide), F14 ("may apply — don't sign yet" banner), F15/F16 (one organiser tile: zero-meeting list, funnel, north star "next steps per recruiter-hour"), F18 (parity chart), F09, F17, F19 (architecture and privacy slides).
- **Not now:** F07 beyond names-after-accept, F12, F20, F11's tasters and credentials; any score, ranking or AI-text detection.

## Tech-challenge fit
- **Nemotron 3.5 Super VL → F01:** the Need Compiler reads a screenshot of Kuura's old job ad, asks two follow-ups and calls the lint (F02) and pool-count (F03) tools; visible: ad in, one-screen card and tool trace out.
- **Modal → F04/F18:** serves Whisper and Gemma on GPU behind the demo URL and fans 1,000 synthetic twins through the F04 extractor; visible: a recorded story becomes quotes, then the parity chart.
- **Gemma → F04:** extracts quote-anchored claims and labelled translations, keeping talent words on an open model the City could self-host; visible: a story told in Arabic reads in English with "show original".

## Three ideas for the Espoo mentors at 09:00
One per job-to-be-done; the pitch leads with the pain they pick.
1. **F01 Need Interview → Challenge Card** — whether account managers would run 12-minute intakes on company visits, and what share of needs arrives in the final week.
2. **F03 Pool Proof** — whether "40+ opted-in people showed this skill" convinces a sceptical SME or feels risky, and whether a consented pool exists at T-21.
3. **F06 Sparks** — whether 3–5 Sparks feel fair to jobseekers and companies will answer every Spark by a deadline; plus real requests-received vs accepted numbers.

## Biggest risk and mitigation
Company effort. Intake, Spark answers, structured conversations and 72-hour closure ask the least-engaged stakeholder for time; if that feels heavier than "send an ad, show up", supply collapses and Sparks point at nothing. Mitigation: a visible ≤ 45-minute company budget outside the event day, tracked as a metric; City account managers run F01 from a pasted ad; Pool Proof pays off before any ask; every company action takes two taps. Validate with mentors at 09:00.
