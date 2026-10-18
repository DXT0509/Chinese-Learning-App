# API conventions

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
