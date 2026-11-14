# Round 3 vote — RAI (Responsible AI, Privacy & Legal Lead)

## Points allocation
| F-ID | Points | Why (≤ 20 words) |
|---|---|---|
| F06 | 25 | The brief's north star: scarce, essay-free requests, blind until accept. AI-free, so no ranking and no Annex III exposure. |
| F01 | 20 | Fixes late, vague needs (P2) weeks ahead; company-side data only; "how each must-have is checked" becomes the conversation script. |
| F04 | 15 | Helps talent articulate value (P5) in their strongest language; no quote, no claim (P6). Supplies what Sparks point at. |
| F03 | 12 | Answers the City's own P1 ("no suitable candidates") with k ≥ 10 bands of shown evidence, never an individual. |
| F02 | 7 | Lints the brief's own bias list (language, nationality, degree, gaps) with legal reasons and pool effect; deterministic, cheap. |
| F10 | 6 | Structured, job-related questions: high validity, low adverse impact; humans judge against the card, talent sees the ticks. |
| F18 | 6 | Turns "polish buys nothing, a foreign name costs nothing" into a measured release gate; our only bias measurement. |
| F13 | 5 | Ends ghosting with job-related reason chips; fading ink makes storage limitation visible; sealed minimal record for discrimination claims. |
| F11 | 4 | Challenge Tables give witnessed proof with little software; pilot at the next event with write-first rules and accommodations. |

## MVP cut (what we build by Sunday 10:00)
- **Build for real** (max 6 F-IDs, in build order): **F01 → F02 → F03 → F04 → F06 → F18.** In each, the deterministic core comes first (card schema, lint rules, banded counts over ~300 synthetic cards, Spark ledger with reveal-on-accept), then the LLM layer with a recorded fallback. F02 and F18 carry the fairness proof and cannot be faked; F10 and F13 mock convincingly.
- **Clickable mock or slide only:** F10 (one-screen conversation sheet, ticks visible to the talent), F13 (two-tap closure with a fading-ink timer), F05 (fact-derived chips on cards), F11 (format slide), F17 + F19 (one trust slide: data-flow map, controllers, AI register, what the AI never does).
- **Not now:** F07 extras (meter, on-device matching), F08 (a fixed slot on accept suffices), F09, F12, F14, F15, F16, F20. Never: scores, rankings, "fits N of M" or AI-text detection.

## Tech-challenge fit
- **Nemotron 3.5 Super VL → F01 (F02, F03 as tools):** reads last year's job-ad screenshot, interviews the manager, calls the lint and pool tools; sees company data only; a planted-proxy eval set measures each prompt revision. Moment: "native Finnish" flagged, pool grows from "fewer than 10" to about 40.
- **Modal → F18 (plus hosting):** public URL, GPU serving for Gemma and Whisper, twin batch fanned out in parallel. Moment: hundreds of plain/polished, name-swapped twins run at once; flip rate shown against the gate.
- **Gemma → F04:** evidence interviewer and labelled translation on open weights the City could self-host, so talent words stay under its control. Moment: an inflated claim refused live — "no quote, no claim".

## Three ideas for the Espoo mentors at 09:00
1. **F01 Need Interview** — could Business Espoo account managers run a 12-minute phone intake three weeks out, and which must-haves do companies really check?
2. **F03 Pool Proof** — on what legal basis may the City show opted-in, k ≥ 10 counts weeks ahead, and would "20+ with evidence" convince a sceptical company?
3. **F06 Sparks** — do 3–5 Sparks feel fair in a public employment service, will companies accept answer deadlines and a cap, and can Sparks stay outside the job-search obligation?

## Biggest risk and mitigation
F04 is the only AI that processes people's own words. If transcription or extraction yields weaker claims for accented or second-language speakers, we rebuild P10 inside our own product, and it may count as Annex III high-risk from 2 Dec 2027. Mitigation: AI asks, never grades; claims are verbatim quote spans the person confirms; editable transcripts and a text option; F18 tests exactly this step against a published flip-rate gate.
