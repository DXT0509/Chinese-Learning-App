# Email/password authentication (Slice 2)

Phase 3 retains these authentication contracts and adds a playable preview lesson UI.
Run responses now include `current_scene_key`; starting the same lesson version resumes
its existing run. See [the vocabulary player guide](vocabulary-player.md).

Email/password registration and login are the MVP priority. Google Sign-In is deferred
until pre-release; no Google SDK, verifier or Google authentication endpoint is included.
`users.id` remains the internal ownership UUID. The new `password_credentials` table
maps a unique normalized email to a user and an Argon2id password hash. Existing users,
Google subjects, legacy email values, progress and SRS schedules are unchanged.

Input emails are trimmed and lowercased, then validated with Pydantic EmailStr. PostgreSQL
requires normalized values and unique credential emails, making login case-insensitive.
This is deliberately a separate login namespace from legacy unverified `users.email`:
registration creates a new UUID even if a legacy row has that email, and never acquires
that row's progress. There is no automatic backfill, credential claim or email-based merge.
Passwords contain 6–128 characters and are never normalized. Argon2id hashing/verification
runs outside the async event loop; missing-account login performs a dummy hash verification.
Errors never echo input or hashes. Duplicate registration returns a generic 409, which
still permits email availability inference; release protections must consider this tradeoff.
Emails are **unverified**, and `/auth/me` explicitly returns `email_verified: false`.

All endpoints below are under `/api/v1`:

| Method | Path | Contract |
| --- | --- | --- |
| POST | `/auth/register` | `{email,password}`; 201 session pair |
| POST | `/auth/login` | `{email,password}`; 200 session pair |
| POST | `/auth/token` | OAuth2 password form: `username` = email, `password`, `grant_type=password`; same session pair |
| POST | `/auth/refresh` | `{refresh_token}`; rotated session pair |
| POST | `/auth/logout` | `{refresh_token}`; revoke family, 204 |
| GET | `/auth/me` | Bearer access token; public account fields only |

For local interactive API use, open `http://127.0.0.1:8000/docs`, click **Authorize**,
enter the existing account email in **username** and the password in **password**,
leave **client_id** and **client_secret** empty, then click **Authorize** and **Close**.
Swagger calls `/api/v1/auth/token` and supplies the returned Bearer access token to
protected requests automatically. JSON `/auth/login` and Android remain unchanged.
The form adapter uses the same email/password validation, authentication service and
router-level rate limiter; it never registers accounts. Clicking Authorize creates a
real session, just like login. Access expires after ten minutes; authorize again when
needed. Swagger Logout clears its authorization; server-side revocation still uses
the existing `/auth/logout` contract. Authorization persistence is not enabled.

Tokens are opaque 256-bit random credentials, not JWTs. `auth_sessions` stores the SHA-256
access digest, 10-minute access expiry, fixed 30-day session expiry and revocation time.
`refresh_credentials` stores only refresh digests and consumption timestamps. Rotation
locks the session row, consumes the old refresh token and replaces the access credential.
Old access credentials immediately stop working. Reusing any consumed refresh token
commits family revocation before returning 401; the newest access and refresh then fail.
Expired/revoked/unknown tokens fail closed. Logout with a recognized family credential
is idempotent, including an already consumed token. Unknown credentials return 401.
The dependency checks the database for every protected request, so revocation is immediate.
Services own transactions; no migrations run at API startup.

Authentication routes have a bounded, per-IP 20-attempt/minute in-process limiter with
429/Retry-After. It uses the connection peer and ignores forwarded headers. **Run one
worker for local development.** A shared/ingress limiter and account-aware abuse controls
are required before multi-worker/public deployment. The current limiter is not distributed.
Responses use `Cache-Control: no-store`. Use the supplied JSON logging configuration and
disabled access logs; do not enable request-body, HTTP credential or SQL parameter logging.

Android uses a Hilt repository with Retrofit and serialized suspend operations. It stores
the session pair in an atomic AES-256-GCM encrypted file in `noBackupFilesDir`, using a
non-exportable Android Keystore key. Private app backup/transfer is disabled. Passwords
exist only in transient form/request memory and are cleared on submission; no SavedState,
Room or DataStore credentials are written. Corrupt/unavailable encrypted storage requires
login again. Domain models contain no transport or Android types.

On 401 the repository refreshes once, atomically saves the rotated pair, then retries the
request once. Refresh rejection clears tokens and returns to login; network/server failures
preserve the pair for retry. A response lost after server rotation, or a process death before
the new pair is stored, may require login again: replay protection takes priority over
silent recovery. Logout requires a successful server revocation (or an already invalid
session); network failure remains visible for retry. Successful logout clears session state,
run state and request IDs. There is no private Room cache or offline synchronization.

App launch restores the saved session before rendering a login or protected navigation graph.
Valid sessions open Home. Missing/rejected sessions open Login. A transient restoration
failure keeps a retry screen without deleting recoverable tokens or flashing Login.
Registration has password confirmation; both registration and login return a real backend
session and open Home. Authentication and protected navigation graphs are discarded on
identity changes, so Back cannot restore Login after success or protected screens after
logout. Account names/emails and available content come from the API. Catalog failures
remain visible on Home without undoing successful authentication.

The shared Android validation policy and backend Pydantic schema accept 6–128 Unicode
characters. Android counts code points, matching Python rather than UTF-16 units. Passwords
and confirmation stay in transient Compose memory; email and non-sensitive screen state can
survive recreation. Field validation stays inline; backend 401/409/422/429 and network errors
appear separately. Six-character registration is covered against real PostgreSQL. The live
OpenAPI schema must report minLength=6; source changes need backend restart or --reload.

The mint Material 3 theme has explicit light/dark palettes, scrollable keyboard-aware forms,
visibility controls and real preview/empty states. Google providers, verification and recovery
are not included. The account area labels unverified email and preview-only learning. Check
preview consent to start/resume a run; server `ALLOW_CONTENT_PREVIEW=true` is also required.
See [USB workflow](android-usb-development.md) and [UI validation report](auth-home-ui-report.md).

Future Google linking must verify official Google tokens with audience/issuer/expiry and
stable `sub`, then attach the identity to the **existing authenticated user UUID** after
explicit linking proof. Matching email alone is insufficient. Existing `google_sub` can
represent that identity without replacing user IDs. Define conflict/recovery policy and
test it before exposing linking; legacy subjectless users need reviewed recovery.

Before public release: implement email verification, password recovery, delivery abuse
protections, password-change/recovery session revocation, a security review, TLS deployment,
shared rate limiting, session-retention/cleanup policy and operational monitoring. Do not
use unverified email as evidence of ownership. Google integration remains pre-release work.

See [Slice 2 verification](slice2-verification.md) for exact commands and test results.
Implementation references: [argon2-cffi API](https://argon2-cffi.readthedocs.io/en/stable/api.html)
and [Android cryptography](https://developer.android.com/privacy-and-security/cryptography).
