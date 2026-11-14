# API contract — Espoo Work Map (v2)

**Superseded.** The v1 TalentMatch Signal contract that lived here was
replaced. The authoritative API definition — data model, endpoints, request
and response shapes, authorisation and derived-label rules — is now
[`app-v2-spec.md`](app-v2-spec.md) **section 3**.

All JSON, prefix `/api`, dev server `http://127.0.0.1:8000`, Vite dev server
`http://127.0.0.1:5173` proxying `/api` → 8000. Synthetic data only.
Session tokens are sent as `Authorization: Bearer <token>`.

v1 is preserved in the git tag `demo-v1` for reference.

## Staff tools (additions after v3)

All advisor-only: residents and employers get `403`, no token `401`.
Counts are aggregates; nothing ranks a person or an advisor. Audit rows
hold ids and outcomes only, never names or contact details.

| Method & path | Body | Returns |
|---|---|---|
| `GET /api/advisor/overview` (extended) | — | adds `outcomes: {last_7_days, all_time}`, each `{help_requests: {new, in_progress, done}, applications, applications_by_advisor, interviews (status interview or offer), offers, event_talks: {recorded, answered, unanswered}, employer_calls: {still_open, filled, no_answer, no_vacancy}}`. `event_talks_unanswered[]` items gain `recorded_by_advisor` |
| `POST /api/advisor/calls` | `{job_id?, employer_id?, outcome: still_open\|filled\|no_answer\|no_vacancy}` | `201 {employer_id, job_id, outcome}`. `still_open` confirms the job (same as `POST /jobs/{id}/confirm`), `filled` closes it (same as `/close`); both need `job_id` (`422` otherwise). Audit `call_logged` with detail `employer_id:job_id\|-:outcome` |
| `GET /api/advisor/employers-to-call` | — | `{employers: [{id, name, contact_name, contact_email, contact_phone, reason: call_again\|no_open_job\|stale, open_jobs, newest_confirmed_days_ago, latest_job_id, last_call: {outcome, at}\|null}]}` — no open job, newest confirmation > 30 days, or last call `no_answer`; an employer who answered a call in the last 30 days is left out. `call_again` first |
| `POST /api/advisor/event/talks` | `{employer_id, first_name, contact_method: phone\|sms\|email, contact_value, job_id?, consent: true}` | `201 {id, employer_id, job_id, status: "talked", recorded_by_advisor: true}`. Walk-up visitor with no account or number; `consent` must be `true` (`422`), employer must have a booth (`404`), job must be theirs (`404`). Appears in `GET /employer/event` talks (with `person_name`, `person_contact_*`, `recorded_by_advisor`) and in the unanswered follow-up. Audit `event_talk_walkup` with the talk id only |
| `GET /api/advisor/event-overview` | — | `{event, employers: [{employer_id, name, booth, visitors_planned, talks, answered, next_step, answered_pct\|null}], totals}` in booth order |

Schema v5: `event_talk.user_id` is nullable; new columns `job_id`,
`visitor_name`, `visitor_contact_method`, `visitor_contact_value`,
`recorded_by`, `consent`. Seed adds `db/seed/employers_unlisted.json`
(three small firms with no job on the map, for the call list).
