# app/web — Espoo Work Map frontend

React 19 + Vite + TypeScript + Tailwind v4, React Router, Leaflet
(`react-leaflet`) for the jobs map. Fonts: Geist Variable (body),
Hedvig Letters Serif (display), Atkinson Hyperlegible (easier-reading mode).
Spec: `docs/03-product/app-v2-spec.md` (authoritative — screens, design, API).

```bash
npm install
npm run dev -- --host 127.0.0.1 --port 5173   # proxies /api -> http://127.0.0.1:8000
npm run build                                  # tsc -b + vite build
npm run lint                                   # oxlint
```

## Screens

| Path | Screen |
|---|---|
| `/` | Jobs — list + map (custom divIcon markers, keyboard-focusable), quick filters, full filters in the URL, empty state with advisor help |
| `/jobs/:id` | Job detail — unified info order, conditions table (yes / no / not known yet, employer vs advisor source), event booth, sticky action bar |
| `/jobs/:id/apply` | Short application — contact, availability, one question, optional CV, per-application need sharing, review & send |
| `/help` | Ask an advisor — works without an account, consent required |
| `/applications` | My applications — status tracker, employer note, waiting days, withdraw |
| `/saved`, `/profile` | Saved jobs · profile with privacy explanation, data download, account deletion, 4-step skippable setup |
| `/sign-in`, `/sign-up` | Auth — demo accounts panel (Aino, Pekka, Amira, Sanna, Leena) |
| `/employer*` | Employer — my jobs, 10-step job form with preview + wording tips, applications grouped by job, company profile |
| `/advisor*` | Advisor — help-request queue, jobs browse/edit/apply-for-someone, condition checks, follow-up |

## Accessibility & i18n

- Every UI string goes through `t()`; `src/i18n/en.ts` and `fi.ts` are complete.
- Accessibility panel: extra-large text, high contrast, easier-reading font,
  reduced motion, Listen buttons (speech synthesis) — state on `<html>`
  `data-*` attributes, styled in `index.css`.
- Nothing under 16 px; verified at 360 px with extra-large text.
- `lib/api.ts` clears the session on 401; route guards keep the return path.
- The list view is the fully equivalent alternative to the map; a skip link
  bypasses it for keyboard users.
