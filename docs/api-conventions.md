# API conventions

## Personal vocabulary API

Phase 3.4 adds authenticated GET/POST `/api/v1/me/vocabulary`, GET `/status` with
`dictionary_entry_id`, and GET/DELETE `/{saved_id}`. Save accepts only a dictionary UUID
and is idempotent per authenticated owner+entry (200). Delete is owner-filtered and returns
204 for absent/foreign/already removed associations; detail returns 404 for absent/foreign IDs.
Listing supports `q`, `limit` (1-50) and a keyset `cursor`; returns `items`, matching `total`,
and `next_cursor`. See [full contracts](personal-vocabulary-design.md).


`GET /api/v1/health` is the primary public liveness route. `GET /health` is an alias.
Both return HTTP 200 and the same documented schema:

```json
{"status":"ok","service":"Chinese Learning API","version":"0.1.0","timestamp":"2026-10-17T00:00:00Z"}
```

Timestamp is generated per request in UTC. This is API process liveness, not database
readiness, session validity or synchronization status. OpenAPI is at `/openapi.json`;
interactive docs at `/docs`. A database readiness endpoint can be added separately.

Unexpected errors return HTTP 500 with `{"detail":"Internal server error"}`.
Invalid requests return 422 with `{"detail":"Invalid request"}`; input values are
never echoed, including passwords/tokens. Unknown routes use 404.
No internal exception text reaches clients. Add safe correlation IDs and centralized
observability before operating this service at scale.

Future routes must live under `/api/v1`, use explicit response models, validate ownership
through authenticated dependencies, and define pagination and retry/idempotency behavior.
Do not accept a user ID in a body as proof of ownership. Slice 2 adds email/password
sessions and protected preview-run/checkpoint endpoints; see [authentication](authentication.md)
and [learning contracts](slice2-verification.md). No completion or mastery APIs are exposed.
Bearer rejection returns 401 with WWW-Authenticate; cross-user runs return 404. Auth
throttling returns 429/Retry-After. Private responses use Cache-Control: no-store.
CORS is closed by default; explicitly enumerate browser origins using a JSON array in
`CORS_ORIGINS`. Native Android requests do not need CORS. Credentialed CORS is disabled.

## Phase 3.1 dictionary lookup

`GET /api/v1/dictionary/search` and `GET /api/v1/dictionary/entries/{entry_id}`
require the existing Bearer identity. Lookup data is shared across users. Search accepts
1–64 codepoints, limit 1–50 and offset 0–1000; exact matches precede prefix matches with
deterministic Unicode ordering. Responses preserve source/revision and nullable Vietnamese
coverage; detail includes source/license attribution. Generic 401/404/422 errors follow
existing policies. See [the full contract](dictionary-foundation.md#http-contracts).
