# Offline and future synchronization

Room is a local public catalog cache. PostgreSQL owns durable cloud data. They do not
synchronize automatically. No background sync worker or remote progress API is present.

When authenticated learning operations are implemented, define an identity-scoped local
model and transactional outbox. A local change and pending operation must commit together.
Each operation needs a stable UUID, account subject, entity identifier, expected revision,
payload version, creation timestamp and retry state. Never reuse an operation UUID for a
different payload. The backend must persist idempotency receipts within the same transaction
as the accepted update and return the prior result for retries.

Use bounded exponential backoff with jitter; retry transient failures, refresh authentication
separately, and surface permanent validation conflicts. Cancel workers before switching
accounts; isolate database partitions (or databases), outbox, cursors and tokens by verified
identity. Never upload one account's pending work under another session. Decide whether
logout discards or securely retains unsent operations and communicate that choice to users.

Use server revisions/cursors and tombstones for incremental pulls. Define conflict rules
per entity: a review event may be append-only, a profile field may require optimistic
concurrency, and SRS state needs server-side reconciliation. Device clock last-write-wins
alone is insufficient. Add WorkManager only when this protocol and a real sync slice exist.
