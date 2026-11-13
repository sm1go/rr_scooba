# 05 — Junction 2026 tech partners: what we plug in

**Status:** updated 14 Nov 2026, 02:00, after the team pasted the prize-bearing tech challenges
(verbatim in `docs/00-challenge/tech-challenges.md`).

## Verified facts

- Junction 2026: 13–15 Nov 2026, Hype Areena, Espoo. Teams of 1–4.
- Platform schedule: preliminary submission Fri 13 Nov 23:55; submissions open **Sat 14 Nov 12:00**;
  **final submission Sun 15 Nov 10:00**; final ceremony Sun 14:00 (challenge winners 15:10).
- "Tech challenges run across every track, so any team can take them on alongside their track." Modal's
  brief adds: "The same project can enter other tech challenges too."
- Each Challenge Partner (incl. City of Espoo) picks its own winners; the main-event winner is chosen by
  peer review (top 5) and a grand jury. Submissions are open-sourced under MIT.
- NVIDIA Build's public model list (checked 14 Nov 2026) includes `nvidia/nemotron-3.5-super-vl-120b-a12b`
  (the model the Nemotron challenge requires), `nvidia/nemotron-3.5-content-safety`,
  `nvidia/nemotron-parse-2.0`, `nvidia/nemotron-3.5-embed-1b`/`-8b`, and Gemma models
  (`google/gemma-4-31b-it`, `google/gemma-3-12b-it`, `google/gemma-3-4b-it`). One OpenAI-compatible
  endpoint can therefore serve both Nemotron and Gemma in the demo (free tier ≈ 40 requests/min per key).

## Prize-bearing tech challenges — fit with our concept

Our direction (Round 1 convergence): voice-to-structured **need cards** for companies, **story / evidence
cards** for talent, scarce **intent tokens**, anonymous **pool counts**, explainable "why this
conversation" sheets, **structured conversations**, an **offline event pass**, and a **fairness dry-run
on synthetic twins**.

| Challenge | What must be true | Natural role in our product | Fit | Effort | Verdict |
|---|---|---|---|---|---|
| **Modal** | Modal does the heavy lifting of a working AI system behind a public URL | Hosts the backend and demo URL; serves open models on GPU (Whisper speech-to-text for voice memos and interviews, Gemma / EmbeddingGemma); fans out the synthetic-twin fairness audit as a batch job | High | Medium | **Go** |
| **Nemotron** (2× RTX 5080) | Nemotron 3.5 Super VL central and visible; write-up on what it does and how outputs were improved | **Need Compiler agent** for companies: reads a pasted job ad, screenshot or PDF (vision), asks follow-up questions, maps needs to ESCO through tools, flags proxy requirements ("native Finnish", degree, nationality), checks k-anonymous pool counts through a tool, drafts evidence questions for structured conversations. An eval set of synthetic job ads with planted proxy requirements gives measured precision/recall across prompt iterations | High | Medium | **Go** |
| **Gemma** | Innovative, impactful use of Gemma open models | Privacy layer: EmbeddingGemma for multilingual matching of need items ↔ evidence — ideally in the talent's browser, so the City never computes a ranking of people (TECH-04) — or on Modal; Gemma for labelled translation of cards | Medium / High | Medium | **Go (scoped)** |
| **Codex** | Codex meaningfully used in the development process, and shown | Second engineering agent: independent review of each milestone, test generation, synthetic-data generator; every use logged in the repo | Medium | Low (needs credits + login) | **Go if credits are claimed** |
| **Gemini API** | "Beyond simply adding an LLM"; explain why Gemini matters | Voice-first story interview in the talent's strongest language (native audio understanding / Live API) → story cards with quoted evidence | Medium | Medium / High | **Stretch** — overlaps with Whisper + Nemotron/Gemma and adds a proprietary provider to the privacy story |
| **ElevenLabs** (MLH, earbuds) | ElevenLabs voices in the project | Spoken prompts in the interview; audio version of the event pass for accessibility | Low / Medium | Low | **Skip** unless time remains |

## Other partners (credits or tools, no prize challenge pasted)

| Partner | Possible use | Note |
|---|---|---|
| Aiven | Managed PostgreSQL (+ pgvector) in an EU/Finnish region | Use only if SQLite on a Modal Volume is not enough |
| Featherless | Hosted open-weight models incl. Finnish **Poro 2** and Gemma | Fallback provider behind the same adapter |
| IronShard | S3 storage with a signed audit log and EU geo-pinning | Nice-to-have evidence of record-keeping |
| CRACI | CI runners with build-time SBOMs | One-line change in CI; procurement-security story |
| Cloudinary | Printable badges, cards and table tents with QR codes | Optional UX |
| Context.dev | Prefill a company card from its domain | **Never** use its people enrichment on talent (C3/C4) |
| Oxylabs | Aggregate public job ads (no personal data) | Low priority |
| Qualia, Scailab, Wendy, Atech.dev, Arduino, Verda | Robotics / hardware / GPU infrastructure | Not relevant (Verda only as an EU GPU host) |

## Recommendation

1. **Core stack: Modal + Nemotron + Gemma**, each with one clearly visible job — Nemotron is the
   company-side Need Compiler agent (tools + vision), Gemma the privacy-preserving matching and
   translation layer, Modal the infrastructure (public URL, GPU inference, fairness batch).
2. **Codex:** use it for reviews and tests during the build and log every use — almost no extra product work.
3. **Gemini and ElevenLabs:** only if the core demo works by Saturday evening.
4. **Responsible-AI framing:** Nemotron and Gemma are open-weight models, so the City could later
   self-host them in the EU without lock-in; the demo uses hosted APIs with synthetic data only.
5. **Engineering rules:** one provider-agnostic adapter (OpenAI-compatible base URL) for all model calls;
   retries with backoff and response caching for the 40 requests/min free tier; each teammate uses
   their own key; a mock provider so that the demo never depends on the network.

## Sources

- [Junction 2026 website](https://2026.hackjunction.com/) · [Junction Platform — Junction 2026](https://hackjunction.app/hackathons/junction-2026) · tech-challenge briefs: `docs/00-challenge/tech-challenges.md`
- [NVIDIA Build model list](https://integrate.api.nvidia.com/v1/models) (public endpoint, queried 14 Nov 2026)
- [Modal](https://modal.com) · [Gemma docs](https://ai.google.dev/gemma/docs) · [Gemini API docs](https://ai.google.dev/gemini-api/docs) · [OpenAI Codex](https://developers.openai.com/codex)
- [Featherless — Llama-Poro-2-8B-Instruct](https://featherless.ai/models/LumiOpen/Llama-Poro-2-8B-Instruct) · [Finnish models on Featherless](https://featherless.ai/models?languages=fi)
- [Aiven](https://aiven.io) · [IronShard](https://www.ironshard.ai/) · [CRACI](https://craci.com) · [Cloudinary](https://cloudinary.com/) · [Context.dev](https://www.context.dev/) · [Oxylabs](https://oxylabs.io)
- [Qualia](https://qualiastudios.dev) · [Scailab](https://www.scailab.se/) · [Wendy](https://wendy.dev/) · [Atech.dev](https://atech.dev)
