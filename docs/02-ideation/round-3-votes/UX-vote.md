# Round 3 vote — UX (Head of Design & User Research)

## Points allocation
| F-ID | Points | Why (≤ 20 words) |
|---|---|---|
| F06 | 22 | Hero interaction: a meeting request without writing a word; kills the AI-essay loop (P6) and recruiter noise (P4). |
| F01 | 17 | Twelve-minute voice or chat intake turns a wish list into three checkable must-haves (P2); every later step reuses them. |
| F04 | 17 | Voice, chat or assisted booth in the strongest language; quotes only; refusing an inflated claim live builds trust. |
| F03 | 12 | Answers P1 in ten seconds ("fluent Finnish: 41 → 6") and nudges out proxies; exposes nobody (k ≥ 10). |
| F13 | 10 | Designs the hardest moment: every connection answered within 72 h; a "no" becomes a warm redirect. |
| F10 | 9 | Event-day proof: same three questions for all, evidence ticks per must-have the talent sees; AI never judges. |
| F11 | 7 | Challenge Tables: a format Espoo can pilot at the next TalentMatch without software; witnessed live beats polished text. |
| F02 | 4 | Turns "fluent Finnish", a core barrier for international talent, into a task × CEFR × "from when" grid. |
| F18 | 2 | One real flip rate for F04 on second-language and AI-polished twins shows we don't rebuild P10. |

## MVP cut (what we build by Sunday 10:00)
- **Build for real** (max 6 F-IDs, in build order): F01 → F04 → F06 → F03 → F10 → F13. One card per side and one thread: Sanna's line "our CI takes 40 minutes" meets Amira's quote "cut build time from 30 to 6 minutes" on every screen. Screens run deterministically on seeded synthetic data first; LLM steps (F01 intake, F04 interview, F13 draft) follow with recorded fallbacks. Accessibility: tap-to-pair (no dragging), a text path for every voice step, plain-language copy.
- **Clickable mock or slide only:** F02 reduced to three lint rules and one language-grid row inside the F01 card; F05 chips as static labels ("told", "witnessed live"); F08/F09 a fixed slot and printable QR pass after "accept"; F11 a printed table tent as a stage prop; F14 one "may apply — don't sign before the decision" banner in F13; F17/F19 one "not used: name, age, photo" receipt and a firewall line; F18 one flip-rate slide from a real batch run.
- **Not now:** F07 beyond reveal-on-accept (already in F06), F12, F15, F16, F20; any score, ranking or AI-text detection.

## Tech-challenge fit
- **Nemotron 3.5 Super VL — F01:** reads a screenshot of Sanna's old job ad, runs the keep-three follow-ups, flags proxies and queries F03 counts as a tool; visible moment: old ad → Challenge Card, count 41 → 6.
- **Modal — F04, F18:** public demo URL, Whisper speech-to-text for the story interview, twin batch fan-out; visible moment: Amira's spoken episode becomes quoted lines she confirms or deletes.
- **Gemma — F04 (+F02):** labelled translation of Finnish or Arabic quotes, original one tap away; visible moment: Sanna toggles a quote between English and the original.

## Three ideas for the Espoo mentors at 09:00
1. **F01 Need Interview** — would account managers run a 12-minute phone intake from the company's old ad, and would a pool count make companies brief three weeks earlier?
2. **F06 Sparks** — do 3–5 refundable requests feel fair to jobseekers, and would companies answer each by a deadline (today: requests received vs accepted)?
3. **F11 Challenge Tables** — would companies host 20-minute problem tables beside booths, and what staffing, accessibility and remote-seat needs would a pilot face?

## Biggest risk and mitigation
Company effort. Intake, Spark answers, structured conversations and 72-hour closure each look light, but together may cost more than "send an ad and show up", and P1's reluctant companies walk. Mitigation: Business Espoo account managers run the intake by phone from the company's existing ad; every company action takes at most two taps; Pool Proof pays off before any ask; the demo shows a running "Sanna's minutes" total, checked against today's effort with the mentors.
