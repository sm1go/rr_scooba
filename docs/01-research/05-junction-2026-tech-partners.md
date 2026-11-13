# 05 — Junction 2026 tech partners: what we could plug in

**Status:** preliminary (14 Nov 2026, 01:40). Based on the public pages only. The tech-challenge
briefs and prize criteria live on the Junction Platform behind login
(`hackjunction.app/participate/45/challenges`) and still have to be pasted into this repo by the team.

## Verified facts

- Junction 2026: 13–15 Nov 2026, Hype Areena, Espoo. Teams of 1–4.
- Platform schedule: preliminary submission **Fri 13 Nov 23:55**; submissions open **Sat 14 Nov 12:00**;
  **final submission Sun 15 Nov 10:00**; final ceremony Sun 14:00 (challenge winners 15:10).
- "Companies provide credits to their platforms, and some of them award prizes to the best use cases
  of their technologies. **Tech challenges run across every track, so any team can take them on
  alongside their track.**" → tech challenges can be stacked on top of the Espoo challenge.
- Each Challenge Partner (incl. City of Espoo) picks its own winners against its own criteria; the
  main-event winner is chosen by peer review (top 5) and a grand jury.
- Submissions are open-sourced under the MIT licence.

## Fit with our direction

Our direction so far (Round 1 convergence): voice-to-structured **need cards** for companies, **story /
evidence cards** for talent, scarce **intent tokens**, anonymous **pool counts**, explainable
"why this conversation" sheets, **structured conversations**, an **offline event pass**, and a
**fairness dry-run on synthetic twins**. Fit is judged against that.

| Partner | What it is | How we could use it | Fit | Effort |
|---|---|---|---|---|
| **Aiven** | Finnish managed open-source data platform (PostgreSQL, OpenSearch, Valkey, Kafka…) | Primary database: PostgreSQL + pgvector for ESCO skill embeddings, hosted in an EU/Finnish region | **High** | Low |
| **Featherless** | Serverless inference for open-weight models, OpenAI-compatible API | Need-card compiler, story → evidence extraction, proxy-requirement lint, labelled translation. Hosts **LumiOpen Llama-Poro-2-8B/70B-Instruct** (Finnish–English, AMD Silo AI + TurkuNLP + HPLT) and Unbabel Tower-Plus-9B (translation) | **High** | Low |
| **Modal** | Serverless GPU/CPU for Python | Whisper speech-to-text for voice memos and story interviews; embeddings; batch synthetic-twin fairness runs; ESCO extraction service | **High / Medium** | Medium |
| **IronShard** | S3-compatible storage for AI agents (MCP), per-agent access control, signed immutable audit log, GDPR geo-pinning | Store consent records and AI-suggestion logs with a signed audit trail — evidence of human oversight and record-keeping | Medium / High (J3) | Low |
| **CRACI** | Secure CI runners with build-time SBOMs and vulnerability monitoring | Run our GitHub Actions on CRACI → SBOM and supply-chain story for public-sector procurement | Medium (J3) | Very low |
| **Cloudinary** | Media API (upload, transform, image/video) | Generate printable "ask me about" badges, story cards and table tents with QR codes; handle voice uploads with auto-deletion | Medium | Low–Medium |
| **NVIDIA** | NIM APIs, Nemotron models, Riva speech, NeMo Guardrails (offer to verify) | Alternative ASR/LLM endpoint; guardrails for PII and protected attributes | Medium | Low–Medium |
| **OpenAI / Codex**, **Anthropic**, **Google DeepMind** | Coding agents and LLM APIs (DeepMind teases something for winning teams) | Build tooling; optional LLM/ASR provider behind the same adapter | Medium | Low |
| **Context.dev** | Web context API: scrape, brand/company data (also people enrichment) | Prefill a company card from its domain (logo, description, industry) → less effort for companies (P2). **Never** use people enrichment on talent (C3/C4) | Medium | Low |
| **Oxylabs** | Web scraping and proxy APIs | Aggregate public job ads (no personal data) to calibrate need cards, e.g. "similar roles in Uusimaa accept English" | Low / Medium | Medium |
| Qualia, Scailab, Wendy, Atech.dev, Arduino | Robot-data understanding, synthetic perception data, edge/physical-AI OS, plug-and-play hardware, Hardware Lab | Only a stretch: a physical "spark" tap point or table timer at in-person events | Low | High |

Verda (Finnish GPU cloud, "AI Infrastructure Track") could host open-weight models in Finland, but it is
presented as a track, not a stackable tech challenge — to verify.

## Preliminary recommendation (pending the prize criteria)

1. **Core:** Aiven (database) + Featherless (Poro 2) + Modal (Whisper and embeddings). All three
   reinforce the responsible-AI story — EU/Finnish infrastructure, open weights the City could
   self-host later, data residency — at low integration cost.
2. **Cheap J3 add-ons:** CRACI (SBOM in CI) and IronShard (signed audit log of AI suggestions and consents).
3. **Optional UX:** Cloudinary for printable badges and cards.
4. **Design rule:** every AI call goes through one provider-agnostic adapter (OpenAI-compatible base
   URL), so the demo can switch between Featherless, NVIDIA NIM, OpenAI or a local mock without code changes.
5. Take on at most 2–3 tech challenges, and only where the partner's technology is visible in the demo.

## Sources

- [Junction 2026 website](https://2026.hackjunction.com/) — partners, schedule, tracks, tech challenges, FAQ.
- [Junction Platform — Junction 2026](https://hackjunction.app/hackathons/junction-2026) — schedule, team size, sponsors.
- [Aiven](https://aiven.io) · [Featherless](https://featherless.ai) · [Llama-Poro-2-8B-Instruct on Featherless](https://featherless.ai/models/LumiOpen/Llama-Poro-2-8B-Instruct) · [Llama-Poro-2-70B-Instruct on Featherless](https://featherless.ai/models/LumiOpen/Llama-Poro-2-70B-Instruct) · [Finnish models on Featherless](https://featherless.ai/models?languages=fi)
- [Modal](https://modal.com) · [IronShard](https://www.ironshard.ai/) · [CRACI](https://craci.com) · [Cloudinary](https://cloudinary.com/) · [NVIDIA](https://www.nvidia.com/en-us/) · [Context.dev](https://www.context.dev/) · [Oxylabs](https://oxylabs.io)
- [Qualia](https://qualiastudios.dev) · [Scailab](https://www.scailab.se/) · [Wendy](https://wendy.dev/) · [Atech.dev](https://atech.dev)
