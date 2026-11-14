# API contract — Espoo Work Map (v2)

**Superseded.** The v1 TalentMatch Signal contract that lived here was
replaced. The authoritative API definition — data model, endpoints, request
and response shapes, authorisation and derived-label rules — is now
[`app-v2-spec.md`](app-v2-spec.md) **section 3**.

All JSON, prefix `/api`, dev server `http://127.0.0.1:8000`, Vite dev server
`http://127.0.0.1:5173` proxying `/api` → 8000. Synthetic data only.
Session tokens are sent as `Authorization: Bearer <token>`.

v1 is preserved in the git tag `demo-v1` for reference.
