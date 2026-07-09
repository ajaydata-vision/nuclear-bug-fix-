# Backend Bug Patterns

Stack-agnostic. Applies to Node.js, Java, Python, Go, Ruby, PHP, or any backend.
Each pattern: symptom → why → how to prove → how to fix.

---

## CATEGORY 1 — API & REQUEST HANDLING

### Pattern: API returns 200 but response body is wrong/empty
**Symptom:** Status 200. Client gets empty data or wrong structure. No error thrown.
**Why:** Handler returns before data is ready. Response serialized before async operation completes. Default empty response sent by framework middleware.
**Prove:** Log the exact response object right before `res.send()` / `return response`. Is it populated?
**Fix:** Ensure all async operations are awaited before responding. Return explicitly — don't rely on framework defaults.

### Pattern: Request body is undefined/empty
**Symptom:** Body parsing works for some routes, not others. `req.body` is undefined or `{}`.
**Why:** Body-parsing middleware not applied. Applied in wrong order. Wrong Content-Type header from client. Multipart form not handled by JSON parser.
**Prove:** Log `req.headers['content-type']` and `req.body` at the start of the handler.
**Fix:** Apply body parser middleware globally and before route definitions. Use correct parser for content-type (JSON vs form vs multipart).

### Pattern: Route not matched — 404 on valid path
**Symptom:** Route defined. Request returns 404.
**Why:** Route order conflict (catch-all before specific route). Method mismatch (POST vs GET). Trailing slash difference. Route prefix not applied. Router not mounted.
**Prove:** Log all registered routes at startup. Or use framework's route listing tool.
**Fix:** Order routes specific → general. Normalize trailing slashes. Verify router is mounted at correct prefix.

### Pattern: Duplicate requests being processed
**Symptom:** One client action causes two DB writes, two emails sent, two charges.
**Why:** Client retrying on timeout. Load balancer retrying. Framework calling handler twice. No idempotency key.
**Prove:** Log a unique request ID at handler entry. Two logs with same ID = duplicate processing.
**Fix:** Implement idempotency keys. Make critical operations idempotent. Deduplicate on unique constraint.

### Pattern: Request timeout but operation completes
**Symptom:** Client gets timeout/504. DB shows the write happened. Or email was sent.
**Why:** Operation takes longer than gateway/load balancer timeout. Client gives up. Server continues processing.
**Prove:** Check server logs vs gateway timeout config. Log operation duration.
**Fix:** Increase timeout for long operations. Or make async: accept request, return job ID, process in background, client polls.

### Pattern: GraphQL query returns 200 with correct shape but is extremely slow — resolver-level N+1
**Symptom:** A GraphQL query for a list with a nested field (e.g. `{ posts { id author { name } } }`) is fast for 1 post, slow for 100 posts, and the slowdown is linear in list size. The query itself, and its returned JSON shape, look completely correct — this is not a wrong-data bug, it's a hidden-cost bug.
**Why:** GraphQL resolvers run independently per field per object by default. The `posts` resolver runs one query to get 100 posts; the `author` resolver then runs once PER post (100 separate queries) because each object in the list is resolved independently with no batching. This is the ORM N+1 pattern (Category 3) but hidden one layer deeper — REST/ORM N+1 is visible by reading the endpoint's code, GraphQL N+1 is invisible in the resolver code because each resolver function looks correct in isolation; the multiplication only happens due to how the GraphQL executor calls them.
**Prove:** Log a query counter (or use APM/tracing) for the duration of a single GraphQL request. Query count scaling linearly with the size of the requested list (not constant) confirms resolver-level N+1. Most GraphQL server frameworks also expose per-resolver timing in their tracing extension — look for one resolver name repeated N times.
**Fix:** Use a batching/caching loader (DataLoader in JS, or the equivalent in your GraphQL server) keyed by the field being resolved, so per-object resolver calls within the same request tick are collected and issued as one batched query:
```js
// DataLoader batches all author lookups requested in the same tick into one query
const authorLoader = new DataLoader(async (authorIds) => {
  const authors = await db.author.findMany({ where: { id: { in: authorIds } } })
  const byId = new Map(authors.map(a => [a.id, a]))
  return authorIds.map(id => byId.get(id))  // must return in the same order as input
})

const resolvers = {
  Post: {
    author: (post, _args, context) => context.authorLoader.load(post.authorId)
  }
}
// authorLoader must be created PER-REQUEST (in context), not module-level —
// a shared loader across requests leaks cached data between users.
```
**Do NOT:** create the DataLoader instance at module scope and share it across requests — that caches one user's data and serves it to the next request.

---

## CATEGORY 2 — AUTHENTICATION & AUTHORIZATION

### Pattern: Token valid but request rejected as unauthorized
**Symptom:** Token clearly not expired. 401 returned. Works in Postman, not in app.
**Why:** Token not sent in correct header. `Bearer ` prefix missing or doubled. Token has extra whitespace/newline. Signature validation failing (wrong secret, wrong algorithm).
**Prove:** Log the raw Authorization header received by server. Compare to what Postman sends.
**Fix:** Log and compare exact token strings. Verify signing secret is same on both sides. Check algorithm (HS256 vs RS256).

### Pattern: Auth works, next request fails
**Symptom:** Login succeeds. First authenticated request works. Subsequent requests fail.
**Why:** Token stored incorrectly on client. Session not persisted. Token refreshed but old token still being sent. Cookie not sent on subsequent requests (SameSite, Secure flags, domain mismatch).
**Prove:** Log the token being sent on the SECOND request. Is it the same as the first? Is it present at all?
**Fix:** Verify cookie flags. Check token storage and retrieval logic. Ensure refresh flow updates token in all places.

### Pattern: Permission check passes but should fail
**Symptom:** User can access resource they shouldn't. Authorization appears to be skipped.
**Why:** Middleware not applied to route. Role check inverted (deny list instead of allow list). Permission checked on wrong field. OR condition where AND was intended.
**Prove:** Add a log inside the permission check: `log("Permission check for user %s on resource %s: %s", userId, resourceId, result)`.
**Fix:** Verify middleware applied to every protected route. Verify logic operators. Default-deny approach: require explicit allow, not explicit deny.

### Pattern: JWT expiry not enforced
**Symptom:** Expired token still grants access. `exp` claim present but not checked.
**Why:** Expiry validation not implemented. Clock skew too large. `exp` field ignored in verification. Wrong field checked.
**Prove:** Create a token with `exp` in the past. Try to use it. Does it succeed?
**Fix:** Always verify `exp` in token validation. Use a well-tested JWT library — don't implement manually. Set clock skew tolerance to minutes, not hours.

---

## CATEGORY 3 — DATABASE & ORM

### Pattern: ORM query returns wrong results
**Symptom:** Query runs. Returns data. Data is wrong — missing rows, extra rows, wrong join.
**Why:** ORM generating wrong SQL. Wrong join condition. Missing WHERE clause. Lazy loading fetching wrong related data. Case sensitivity in string comparison.
**Prove:** Enable ORM query logging. Print the actual SQL being generated. Run it directly in DB client.
**Fix:** Fix the ORM query. Or use raw SQL for complex queries. Verify with `EXPLAIN` that query plan is correct.

### Pattern: N+1 queries from ORM
**Symptom:** Page load slow. DB CPU spikes. Works for small data, breaks under load.
**Why:** ORM fetches parent records, then fetches each child individually in a loop.
**Prove:** Log total query count per request. Count should be O(1) not O(n).
**Fix:** Use eager loading (`.include()`, `.with()`, `JOIN FETCH`). Batch the child queries with `WHERE id IN (...)`.

### Pattern: Migration succeeds but schema wrong
**Symptom:** Migration runs without error. App behaves as if column/table doesn't exist.
**Why:** Migration ran on wrong database. Multiple schemas — migrated wrong one. ORM model not updated to match migration. Migration ran in transaction that was rolled back.
**Prove:** Connect directly to DB. Run `\d tablename` (Postgres) or `DESCRIBE tablename` (MySQL). Is the column there?
**Fix:** Verify migration target DB. Sync ORM model with actual schema. Check migration logs for rollback.

### Pattern: Unique constraint violation in race condition
**Symptom:** Works under low load. `UNIQUE constraint failed` errors under concurrent traffic.
**Why:** Check-then-insert pattern: two requests both check, both see no conflict, both insert. Classic TOCTOU race.
**Prove:** Simulate concurrent inserts with two requests at same time. Error appears.
**Fix:** Use `INSERT ... ON CONFLICT DO NOTHING/UPDATE`. Or use DB unique constraint as the only check — catch the constraint error and handle it.

---

## CATEGORY 4 — BACKGROUND JOBS & QUEUES

### Pattern: Job enqueued but never executed
**Symptom:** Job added to queue. Worker running. Job sits in queue forever.
**Why:** Worker not consuming from correct queue name. Worker crashed silently. Job picked up but thrown back due to deserialization error. Worker concurrency = 0.
**Prove:** Log queue name when enqueuing AND when worker starts consuming. Are they identical strings?
**Fix:** Verify queue names match exactly (case-sensitive). Check worker process is alive. Log deserialization of job payload.

### Pattern: Job silently fails — no error logged
**Symptom:** Job consumed (removed from queue). No result. No error. Nothing happened.
**Why:** Error caught and swallowed inside job handler. Job marked complete before operation finishes. Exception in async code not propagated.
**Prove:** Add try/catch wrapping the entire job handler. Log ALL errors including stack trace.
**Fix:** Never swallow errors in job handlers. Re-throw or mark job as failed. Use dead-letter queue for failed jobs.

### Pattern: Job executed multiple times
**Symptom:** One enqueue → multiple executions. Duplicate emails, duplicate charges.
**Why:** Job not acknowledged before timeout. Worker processes job, crashes before ACK. Message broker re-delivers. No idempotency guard.
**Prove:** Add unique job ID. Log at start of execution. Multiple logs with same ID = duplicate.
**Fix:** Implement idempotency in job handler (check if already processed). ACK/delete message AFTER successful processing. Use atomic check-and-process.

### Pattern: Cron job runs at wrong time
**Symptom:** Cron job doesn't run when expected. Or runs at unexpected times.
**Why:** Cron expression wrong. Server timezone ≠ intended timezone. Multiple instances all running the job. DST transition causes skip or double-run.
**Prove:** Log the next scheduled run time at startup. Compare to expectation.
**Fix:** Test cron expressions at crontab.guru. Set timezone explicitly in cron config. Use distributed lock to prevent multi-instance double-run. Use UTC always.

---

## CATEGORY 5 — FILE HANDLING & UPLOADS

### Pattern: File upload succeeds, file not accessible
**Symptom:** Upload API returns success. File not found when trying to retrieve.
**Why:** File saved to local disk of one instance (not shared storage). Temp directory cleaned up. Path constructed incorrectly. Permissions wrong.
**Prove:** Log absolute path where file is saved. Then log path where retrieval looks. Are they the same?
**Fix:** Use shared storage (S3, NFS, object store) not local disk in multi-instance setups. Return full path from save operation.

### Pattern: Large file upload fails or times out
**Symptom:** Small files work. Large files fail mid-upload or return 413/timeout.
**Why:** Body size limit too small. Request timeout too short. No streaming — entire file loaded to memory. Proxy timeout (nginx, load balancer).
**Prove:** Check error response headers. Is it 413 (too large) or 504 (timeout)?
**Fix:** Increase body size limit in framework AND reverse proxy. Implement streaming/chunked upload for large files. Increase proxy timeout.

### Pattern: File content corrupt after upload/download
**Symptom:** File uploads successfully. Downloaded file is corrupt or truncated.
**Why:** Binary file treated as text (line ending conversion). Encoding mismatch. Incomplete read. Base64 encoding/decoding error.
**Prove:** Compare file size before upload and after download. Check MD5/SHA of both files.
**Fix:** Use binary mode for all file I/O. Avoid any text encoding for binary files. Validate checksum after transfer.

---

## CATEGORY 6 — SESSION & STATE MANAGEMENT

### Pattern: Session data lost between requests
**Symptom:** Login works. Next request — user treated as logged out. Session empty.
**Why:** Session stored in memory (lost on restart or different instance). Session ID cookie not sent. Session store connection failing silently.
**Prove:** Log session ID on login AND on next request. Same ID but empty session = store issue. Different ID = cookie not persisted.
**Fix:** Use external session store (Redis, DB). Verify cookie settings. Check session store connection.

### Pattern: Session shared between users
**Symptom:** User A sees User B's data. Session contamination.
**Why:** Session not isolated per user. Object shared across requests (module-level mutable state in some frameworks). Cache key collision.
**Prove:** Log user ID from session on every request. Look for mismatches between session user ID and request user ID.
**Fix:** Never store user state in module-level variables in server code. Always scope state to session/request. Validate session belongs to requesting user.

---

## CATEGORY 7 — RATE LIMITING & THROTTLING

### Pattern: Rate limit triggered for legitimate users
**Symptom:** Users get 429 Too Many Requests. They're not abusing the API.
**Why:** Rate limit keyed on IP, but users behind NAT/proxy share IP. Limit too strict. Mobile users on carrier NAT. CDN forwarding same IP.
**Prove:** Log the key being used for rate limiting. Is it the real user IP or a proxy IP?
**Fix:** Use `X-Forwarded-For` header (trust carefully). Rate limit by user ID for authenticated endpoints. Increase limit or use sliding window algorithm.

### Pattern: Rate limit not triggering despite high traffic
**Symptom:** Rate limit configured. Abuse occurring. No 429s returned.
**Why:** Rate limit middleware not applied to the right routes. Counter stored in memory (lost between restarts, not shared between instances). Wrong key being used.
**Prove:** Manually send 100 rapid requests. Do 429s appear? Check which instance each request hit.
**Fix:** Store rate limit counters in Redis (shared between instances). Apply middleware to correct routes. Verify key extraction.

---

## CATEGORY 8 — LOGGING & OBSERVABILITY

### Pattern: Error occurs but logs show nothing
**Symptom:** Bug is real and reproducible. Logs are clean. No errors visible.
**Why:** Log level set too high (WARN/ERROR only, error logged at DEBUG). Error swallowed before logger reached. Logs going to different sink. Async error not propagated to global handler.
**Prove:** Set log level to TRACE/DEBUG. Run again. Look for hidden errors.
**Fix:** Log ALL caught exceptions with full stack trace. Set appropriate log levels. Add global unhandled exception/rejection handlers.

### Pattern: Logs out of order — cannot trace request
**Symptom:** Logs arrive but sequence is wrong. Cannot correlate logs from same request.
**Why:** Async operations interleave log output from different requests. No request ID in logs.
**Prove:** Make two concurrent requests. Try to trace each one through logs. Can you separate them?
**Fix:** Generate a unique request ID at entry. Include it in every log statement for that request. Use async context / correlation ID propagation.

---

## CATEGORY 9 — EXTERNAL SERVICE INTEGRATION

### Pattern: External API call succeeds in dev, fails in prod
**Symptom:** Same code, same API key. Works locally. Fails in production.
**Why:** Outbound firewall blocking in prod. API key for wrong environment. IP allowlist on external service. SSL certificate validation failing in prod.
**Prove:** From prod server: `curl -v https://external-api.com/endpoint`. Does it connect?
**Fix:** Open firewall for outbound to external service. Use correct API key per environment. Whitelist prod server IP with external service.

### Pattern: Third-party webhook not being received
**Symptom:** External service sends webhook. Your server never processes it.
**Why:** Endpoint not publicly accessible. Wrong URL registered. Signature validation rejecting all webhooks. SSL issue. Endpoint returning non-2xx (external service stops retrying).
**Prove:** Check external service's webhook delivery logs — is it showing success or failure? What response code is it getting?
**Fix:** Ensure endpoint is publicly accessible. Return 200 immediately, process async. Fix signature validation. Use webhook testing tools (ngrok for local dev).
**See also:** `references/integration-patterns.md` Category 1 has four more specific webhook patterns (signature validation with raw-body gotchas, silent no-op processing, duplicate processing, out-of-order delivery) — load it alongside this file for any webhook bug beyond simple non-delivery.

---

## CATEGORY 10 — CONNECTION POOLING

### Pattern: Requests time out under load but succeed at low traffic
**Symptom:** API works at low traffic. Under load, requests queue and time out. DB CPU normal. App CPU normal. Pool queue length grows continuously.
**Why:** Pool exhausted. Slow queries hold connections for their full duration. Max throughput = pool_size ÷ avg_query_duration. Any traffic above this queues indefinitely.
**Prove:** Log pool queue length every 5 seconds under load. Log query duration per DB call. Calculate: connections × avg query time = throughput ceiling. Compare to actual request rate.
**Fix:** Optimise slow queries first (indexes, reduce result set). Tune pool size to match DB `max_connections`. Set pool acquisition timeout so queued requests fail fast rather than waiting silently. Consider read replicas for read-heavy workloads.

### Pattern: Connection pool exhausted with only a handful of active requests
**Symptom:** Pool exhausted even with 3-5 concurrent requests. Pool size is 20. Idle count trends downward over time without recovering.
**Why:** Connections acquired and never released. Missing `finally` block — exception path skips `client.release()`. Long-running transactions holding connections. Leak accumulates over hours.
**Prove:** Log pool stats (total, idle, waiting) on every request entry and exit. Idle count should return to pre-request level after each request completes. Trending downward = leak.
**Fix:** Always release in `finally` block or use a pool wrapper that guarantees release. Never acquire a connection outside try/finally. Set a connection timeout so leaked connections are reclaimed automatically.

### Pattern: Increasing pool size does not improve performance
**Symptom:** Pool size raised from 10 to 50. Timeouts persist. DB shows more connections but same wait time. DB CPU increases.
**Why:** DB itself is the bottleneck. Beyond the DB's optimal concurrency, more connections cause lock contention and context-switch overhead — hurting not helping.
**Prove:** Check DB CPU and I/O while adding connections. Run `SHOW max_connections` and `SELECT count(*) FROM pg_stat_activity` (Postgres). DB CPU rising with pool size = DB saturation.
**Fix:** Pool size ≠ throughput. Optimise queries. Cache hot reads. Batch writes. For Postgres: optimal pool size is often `(2 × CPU cores) + spindle_count` — not an arbitrary large number.

---

## CATEGORY 11 — DISTRIBUTED LOCKING

### Pattern: Critical section executed by two processes simultaneously
**Symptom:** Two workers process the same job. Duplicate charges, records, or data corruption. Only under concurrent load with multiple instances.
**Why:** No mutual exclusion. Read-check-write is not atomic: both processes read the same state before either writes. Classic TOCTOU race.
**Prove:** Log `hostname + pid + timestamp` at the start of the critical section. Two log entries within milliseconds from different hosts = race confirmed.
**Fix:** Use `SELECT FOR UPDATE SKIP LOCKED` (Postgres) to atomically claim a row — only the row that is claimed gets processed. Or Redis `SET key value NX EX ttl` — atomic set-if-not-exists with expiry. Only one process succeeds.

### Pattern: Distributed lock acquired but never released — permanent block
**Symptom:** Operation permanently blocked. Redis/DB shows a lock key that never expires. The process that set it crashed.
**Why:** Lock set without TTL. A crashed process cannot release what it holds. Without TTL, the lock persists until manually deleted.
**Prove:** `redis-cli TTL lock:key` returns -1 (no expiry) = permanent lock. Check when the key was created vs when the holding process died.
**Fix:** Always set the lock atomically with expiry: `SET lock:key value NX EX 30`. TTL must be longer than the maximum expected operation duration. Add a stale lock alert: if a lock is older than 2× its expected duration, page someone.

### Pattern: Lock expires while operation still running — two holders simultaneously
**Symptom:** TTL set to 30 seconds. Operation sometimes runs 35 seconds. Second process acquires the lock while first still holds it. Data corruption follows.
**Why:** TTL shorter than the P99 operation duration. Lock expires, second process acquires it, both run simultaneously.
**Prove:** Log operation start and end time. Compare to lock TTL. Any run exceeding TTL = unsafe window.
**Fix:** Set TTL to 3× P99 operation duration. Implement lock heartbeat: holding process extends TTL every N seconds while still running (`EXPIRE lock:key ttl`). Use Redlock for multi-node Redis.

---

## CATEGORY 12 — SECURITY PATTERNS

### Pattern: Session fixation — attacker hijacks session after login
**Symptom:** After login, the session ID is identical to the pre-login session ID. An attacker who planted that session ID can now access the authenticated session.
**Why:** Session ID not regenerated on privilege escalation. The existing session is reused with elevated privileges attached.
**Prove:** Log session ID before and after `POST /login`. If identical → vulnerable.
**Fix:** Call `session.regenerate()` immediately on successful login. New session ID must be different and unpredictable. Old session must be invalidated. This is a one-line fix in express-session.

### Pattern: CSRF attack succeeds on state-changing endpoint
**Symptom:** Authenticated endpoint triggerable from a third-party site via form or fetch. No CSRF token required. Browser sends cookies automatically.
**Why:** Without a CSRF token or SameSite cookie, any site can forge requests as the authenticated user. Browser cookie policy is the only gate — and it's insufficient for legacy SameSite=None.
**Prove:** From a different origin, submit a form targeting the API endpoint. Does it succeed?
**Fix:** Use `SameSite=Strict` or `SameSite=Lax` cookies. For APIs: require a CSRF token in a custom header (`X-CSRF-Token`) that cannot be set cross-origin. Or use the Double Submit Cookie pattern.

### Pattern: JWT algorithm confusion — HS256 vs RS256 auth bypass
**Symptom:** Tokens signed with RS256 (asymmetric) accepted when re-signed with HS256 using the server's public key as the HMAC secret. Critical auth bypass.
**Why:** Server accepts multiple algorithms. Attacker signs a forged token with HS256 using the public key (which is public) as the secret. Server validates it as HS256 and accepts it.
**Prove:** Take the server's public key. Sign a forged JWT with HS256 using that key as HMAC secret. Does the server accept it?
**Fix:** Specify exactly one expected algorithm in verification: `algorithms: ['RS256']` — never a list mixing HS256 and RS256. Reject tokens where `alg` header doesn't match. Never accept `alg: none`.

### Pattern: IDOR — user accesses another user's data via ID manipulation
**Symptom:** User A accesses User B's records by changing an ID in the URL or request body. No error returned. Authorization checks authentication but not ownership.
**Why:** Endpoint verifies the user is logged in but never verifies the requested resource belongs to that user.
**Prove:** Log in as User A. Note User A's resource IDs. Request a resource ID belonging to User B. Does it return data?
**Fix:** After loading the resource, always verify `resource.ownerId === req.user.id`. Never trust client-supplied IDs for ownership. Default-deny: if ownership check is missing, deny the request.
