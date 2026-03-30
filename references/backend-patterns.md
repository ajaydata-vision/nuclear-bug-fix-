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
