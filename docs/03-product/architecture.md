# Architecture — TalentMatch Signal (MVP for Junction 2026)

**Status:** draft, 14 Nov 2026 ~02:15. The MVP scope is confirmed after the Round 3 vote
(`shortlist.md`). Design principle from the brief and Round 2: **the deterministic spine first**
(cards, counts, Sparks, conversations, closure on synthetic data), then AI steps that only *suggest*,
each with a recorded fallback so the demo never depends on the network.

## Components

```text
            ┌──────────────────────── Modal (one app, public URL) ────────────────────────┐
 browser ──▶│ FastAPI web app  ── serves the React build + /api                            │
 (React,    │   ├─ rules: requirement lint · k-anonymous pool bands · Sparks · scheduler   │
 PWA pass)  │   ├─ SQLite on a Modal Volume (synthetic data only)                          │
            │   └─ LLM adapter (OpenAI-compatible) ──┬─▶ NVIDIA Build: Nemotron 3.5 Super VL│
            │                                        ├─▶ Gemma on Modal GPU (vLLM)          │
            │                                        └─▶ mock provider (recorded outputs)   │
            │ Whisper on Modal GPU (voice memos, optional)                                 │
            │ Twin-test batch: fan-out of synthetic twins through the extraction step      │
            └──────────────────────────────────────────────────────────────────────────────┘
```

| Part | Choice | Why |
|---|---|---|
| Frontend | React + Vite + TypeScript + Tailwind, served as static files by the API | Polished UI quickly; one deployable |
| Event pass | Static page + service worker, QR | Works offline on the event day (P8) |
| Backend | Python FastAPI | Already on the dev machine; same language as the Modal jobs |
| Database | SQLite, seeded from `db/seed/*.json` | Synthetic data only (C2); zero ops; schema in `db/schema.sql` |
| Hosting | Modal (`modal deploy`) | Public URL, GPUs, batch fan-out — *Best use of Modal* |
| Company agent | **Nemotron 3.5 Super VL** (`nvidia/nemotron-3.5-super-vl-120b-a12b`) via NVIDIA Build | Reads ads, screenshots and PDFs, calls our tools — *Best use of Nemotron* |
| Talent-side extraction | **Gemma** served on Modal with vLLM (NVIDIA-hosted Gemma as fallback) | Open weights the City could self-host; high throughput for the twin test — *Gemma* + *Modal* |
| Skills taxonomy | ESCO subset cached as JSON (CC BY 4.0) | Common language for needs and evidence |
| Build process | Codex for independent reviews and tests, logged | *Best use of Codex* |

## AI steps — what they may and may not do

| Step | Model | Input → output | Human control | Guard |
|---|---|---|---|---|
| Need Compiler (F01, F02, F03) | Nemotron 3.5 Super VL with tools `esco_search`, `pool_preview`, `lint_requirements`, `submit_card` | Pasted ad, screenshot or voice transcript → draft Challenge Card (90-day problem, 3 must-haves with "how we'll check it", language needs as task × CEFR × from-when) | Company edits and approves; lint hints never block | Pydantic schema; never infers protected attributes; every call logged |
| Story interview (F04) | Gemma | Story transcript → ≤ 3 follow-up questions; then claims, each with an **exact quote** | Person confirms or deletes every claim | Server checks the quote is a substring of the transcript ("no quote, no claim"); verb-strength check against inflation ("helped" ≠ "led") |
| Twin test (F18) | Gemma on Modal, batched | Synthetic twins (plain vs AI-polished, name and language swaps) → extracted claims → flip rate | Organiser sees the report; release gate threshold | Runs on synthetic data only |

Never: scores or rankings of people, AI-text detection, emotion or voice analysis, eligibility for
public support before selection, linking event data to benefit registers.

## Deterministic rules (unit-tested)

- **Pool bands:** counts of consenting registrants with a *confirmed* claim for each must-have and the
  required language level; shown as "fewer than 10", "10–19", "20–49", "50+" (k = 10); plus the count
  with each must-have removed (elasticity). Never a list of people.
- **Requirement lint:** a rulebook of triggers (native speaker, nationality, age, gendered words, photo,
  unexplained degree, "no gaps", "cultural fit") → at most five hints with the legal reason
  (Non-Discrimination Act 1325/2014, Equality Act 609/1986) and a suggested rewrite.
- **Sparks:** 3 per talent per event; each pairs one confirmed claim with one card requirement; the
  company answers by a deadline or the Spark is refunded; the name is revealed only on accept.
- **Scheduler:** greedy over mutual yeses, in rounds so that everyone gets a first meeting before anyone
  gets a fourth, within the real slot capacity.
- **Closure:** two taps with job-related reason chips taken from the card; warm redirect; content fades
  after 30 days, a sealed minimal outcome record is kept for the claim period.

## Data model (SQLite, synthetic)

`event`, `company`, `challenge_card`, `card_requirement`, `talent` (pseudonymous; languages with CEFR;
pool consent), `talent_identity` (kept apart; revealed only after a mutual yes), `evidence_card`,
`evidence_claim` (quote, ESCO URI, evidence level, confirmed), `spark`, `meeting`, `conversation_tick`,
`closure`, `audit_log` (every AI suggestion and every human decision).

## Repository layout

```text
app/api/        FastAPI app: routers, rules, LLM adapter, agents
app/web/        React frontend
app/modal_app.py  Modal deployment (web app, Gemma vLLM, Whisper, twin batch)
db/             schema.sql, seed/*.json (generated), esco/*.json
scripts/        generate_synthetic.py, fetch_esco_subset.py
evals/          need-compiler eval set + runner (for the Nemotron write-up)
tests/          pytest: lint, pool bands, Sparks, scheduler, quote guard, twin parity
```

## Configuration (`.env`, git-ignored)

`NVIDIA_API_KEY`, `LLM_PROVIDER` (`nvidia` | `modal` | `mock`), `GEMMA_BASE_URL`, `MODAL_*`
(via `modal setup`), optional `OPENAI_API_KEY` for Codex. Every model call goes through one adapter
with retries, backoff and a response cache (NVIDIA's free tier allows about 40 requests per minute).
