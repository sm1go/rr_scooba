# Round 3 vote — TECH (CTO & AI/ML Lead)

## Points allocation
| F-ID | Points | Why (≤ 20 words) |
|---|---|---|
| F06 | 25 | Headline mechanic: scarce, evidence-paired requests cut AI-generated noise (P4, P6); no AI, deterministic, self-explaining in ten seconds. |
| F01 | 20 | Fixes late, vague needs (P2) at the root; its "how will you check it" feeds Sparks, conversations and closure. |
| F04 | 15 | Talent half of every Spark: "no quote, no claim" makes polish worthless; voice or text, strongest language (P5, P6). |
| F03 | 12 | Answers "no suitable candidates in the City's pool" (P1) with banded k ≥ 10 counts; deterministic, exposes nobody. |
| F10 | 8 | Event day runs on the card: same three questions, one-tap anchored ticks, "witnessed live" evidence; AI never judges. |
| F02 | 6 | Deterministic proxy lint with legal reasons; "fluent Finnish: under 10 → Finnish B1: 20+" is our fairness moment (P10). |
| F13 | 5 | An answer within 72 hours and warm redirects make the free City service feel high-quality (P1, P5); two taps. |
| F05 | 4 | Answers the AI question with process-derived evidence levels, not detection; one chip component, never a score or filter. |
| F11 | 3 | Memorable format for real events, but facilitation rather than software: narrate Challenge Tables; work samples need parity checks. |
| F18 | 2 | Runs F04 extraction on synthetic twins (plain vs polished, other language): polish must buy nothing; one Modal batch. |

## MVP cut (what we build by Sunday 10:00)
- **Build for real** (max 6 F-IDs, in build order): **F06 → F03 → F02 → F01 → F04 → F10** — deterministic spine first on seeded synthetic data, then the two LLM steps.
  - F06: 5 Sparks per talent, quote × card-line pairs, deadline refunds, names only after accept.
  - F03: banded counts (k ≥ 10, fixed query shapes) over ~300 synthetic opted-in profiles.
  - F02: ~15 curated rules; at most 5 hints, each with legal reason and pool effect.
  - F01: pasted ad, screenshot or voice transcript → Nemotron agent → schema-valid card with ESCO-tagged must-haves; F02 and F03 as tools.
  - F04: Whisper or text → Gemma proposes claims with quote spans; a deterministic guard drops unquoted ones; the talent confirms or deletes each line.
  - F10: conversation screen generated from the card; ticks set the "witnessed live" chip.
- **Clickable mock or slide only:** F13 (two-tap closure, reason chips, company-approved draft), F05 (only "own words" and "witnessed live" chips; full ladder on a slide), F11 and F14 (one slide each), F09 (architecture slide: pre-generated agendas, offline QR pass), F18 (parity table from a real Modal batch), F19 (one line on the privacy slide).
- **Not now:** F07 beyond F06's name-after-accept, F08 (accepted Sparks pick a free slot), F12, F15, F16, F17, F20.

## Tech-challenge fit
- **Nemotron 3.5 Super VL → F01 (F02, F03 as tools):** a screenshot of last year's job ad becomes a Challenge Card live, "native Finnish" flagged with its pool effect; a planted-proxy eval set documents prompt improvements.
- **Modal → F04 and F18, plus hosting:** public demo URL, Whisper and Gemma on GPU, the twin batch fanned out; visible moment: a voice story transcribed in seconds, then the parity table.
- **Gemma → F04:** open-weight, City-hostable interviewer asking follow-ups in the talent's language and proposing quote-anchored claims; visible moment: each claim beside Amina's own words, an inflated one refused by the guard.

## Three ideas for the Espoo mentors at 09:00
1. **F01** — When and in what form do needs arrive today, and would Business Espoo account managers run a 10-minute intake call weeks earlier?
2. **F06** — Would a 3–5 Spark cap feel fair for a public service, and how many requests does a company receive vs. accept today?
3. **F03** — Would a banded count convince a sceptical company, and may the City count opted-in registrants' evidence (legal basis, DPO)?

## Biggest risk and mitigation
Six features and two live LLM steps in ~20 hours; if F01 or F04 stalls on stage (≈40 requests/min, latency, a misheard accent), the concept looks fake. Mitigation: deterministic spine first on one schema and one demo story; schema-constrained calls behind one adapter; quote guard outside the model; every LLM step cached with a recorded fallback, text beside voice; F18 twins and injection strings tested on F04; if we slip, F10 stays a mock; feature freeze Sunday 06:00.
