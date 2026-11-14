# TalentMatch Signal — web (React)

Frontend of the hackathon MVP. Vite + React 19 + TypeScript + Tailwind v4, react-router, lucide-react, Inter.
API contract: `docs/03-product/api-contract.md`. Design rules: `docs/03-product/design-guide.md`.

```bash
npm install
npm run dev -- --host 127.0.0.1 --port 5173   # proxies /api -> http://127.0.0.1:8000
npm run build                                   # tsc -b + vite build
npm run typecheck                               # tsc -b (project references)
npm run lint                                    # oxlint
```

If the API is not reachable, every call falls back to synthetic fixtures in `src/fixtures/` (mirroring
`db/seed`) and the top bar shows a quiet "Demo data (offline)" badge. JSON 4xx errors from a running API
(e.g. 409 Spark budget used) are shown to the user, never replaced by fixtures.

## Map

| Path | Screen |
|---|---|
| `/` | Landing — the three roles |
| `/company` | 1. Describe your need (paste ad / screenshot → `POST /api/compiler/draft`) |
| `/company/card` | 2. Card editor, lint notes, Pool Proof, approve |
| `/company/sparks` | 3. Sparks inbox (Accept / Not now + reason chip) |
| `/company/meetings`, `/company/meetings/:id`, `…/closure` | 4. Meetings → conversation sheet → 72-hour closure |
| `/talent` | 5. Tell a work story → follow-ups → quote-backed claims → save |
| `/talent/sparks` | 6. Browse cards and send a Spark; My Sparks |
| `/organiser` | 7. Overview tiles, Trust lab, audit log |

## Source layout

- `src/api.ts` — typed client + offline fallback; `src/types.ts` — contract types.
- `src/components/` — layout (top bar, role switcher, footer), small UI kit, claim view.
- `src/pages/company/hints.ts` — where a lint hint sits on the card and what "Use suggestion" changes.
