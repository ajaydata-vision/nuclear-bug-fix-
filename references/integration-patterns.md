# Integration & Pipeline Bug Patterns

Stack-agnostic. Applies to any message broker, microservice architecture, ETL pipeline, or CI/CD system.
Each pattern: symptom → why → how to prove → how to fix.

---

## CATEGORY 1 — WEBHOOKS

### Pattern: Webhook registered but never received
**Symptom:** External service shows webhook configured. Your endpoint shows no traffic.
**Why:** Endpoint not publicly reachable. Wrong URL registered (typo, wrong env, HTTP vs HTTPS). Firewall blocking inbound. External service using old URL after update.
**Prove:** Check external service's delivery log — is it even attempting delivery? What URL is it calling?
**Fix:** Test endpoint accessibility from public internet (not localhost). Use webhook inspection tools. Re-register correct URL. Open inbound port.

### Pattern: Webhook received but signature validation fails
**Symptom:** Request arrives (confirmed in logs). Returns 401/403. Signature mismatch.
**Why:** Raw body not used for signature computation (body-parser already parsed it). Wrong secret. Wrong algorithm. Extra whitespace in secret. Encoding difference (hex vs base64).
**Prove:** Log the raw body bytes AND the secret (redacted). Manually compute the expected signature. Compare.
**Fix:** Read raw body BEFORE JSON parsing for signature verification. Use framework's raw body option. Verify secret has no extra whitespace.

### Pattern: Webhook processed but no action taken
**Symptom:** Webhook received. Returns 200. No business logic executed.
**Why:** Event type filter too strict — webhook event not in allowed list. Handler routing by wrong field. Event payload structure different from expected.
**Prove:** Log the full incoming webhook payload. Log which event type was detected. Log the branch taken.
**Fix:** Log all received event types. Compare to what you're filtering for. Update filter or handler.

### Pattern: Webhook processed multiple times
**Symptom:** One external event causes duplicate processing (two emails, two charges).
**Why:** External service retries on timeout or non-2xx. Your server takes too long to respond. No idempotency check.
**Prove:** Check external service retry logs. Log webhook event ID on every receipt. Multiple logs with same ID = duplicate.
**Fix:** Respond 200 immediately. Process async. Store processed event IDs. Reject duplicates with 200 (not 4xx — that causes more retries).

### Pattern: Webhook delivery ordering not guaranteed
**Symptom:** Events arrive out of order. State becomes inconsistent.
**Why:** External service doesn't guarantee ordering. Retries cause earlier event to arrive after later one. Different delivery workers.
**Prove:** Log webhook event timestamp and receipt timestamp. Compare sequence.
**Fix:** Include event sequence number or timestamp in payload. Process events idempotently. Build state machine that handles out-of-order events gracefully.

---

## CATEGORY 2 — MESSAGE QUEUES & EVENT STREAMING

### Pattern: Message published but consumer never receives it
**Symptom:** Producer confirms publish. Consumer log shows nothing.
**Why:** Consumer subscribed to wrong topic/queue name. Consumer in wrong consumer group. Topic not created. Message expired before consumer started. Partition assignment issue.
**Prove:** Use queue admin tool to inspect: Is message in the queue? Is consumer connected to correct queue?
**Fix:** Verify exact topic/queue name match (case-sensitive). Check consumer group config. Verify topic exists before publishing. Increase message TTL.

### Pattern: Message consumed but processing fails silently
**Symptom:** Message removed from queue. No error logged. No business effect.
**Why:** Error swallowed in consumer handler. Message acknowledged before processing. Deserialization failing silently and returning null/empty.
**Prove:** Add try/catch wrapping ENTIRE consumer handler. Log ALL errors. Log the raw message payload.
**Fix:** Never swallow consumer errors. Acknowledge AFTER successful processing. Use dead-letter queue for failures. Log deserialization separately.

### Pattern: Consumer lag growing — messages piling up
**Symptom:** Queue depth increasing. Consumers running. Processing falling behind.
**Why:** Consumer too slow (DB bottleneck, slow external call). Not enough consumer instances. Single-threaded consumer. Message processing taking longer than expected.
**Prove:** Log processing time per message. Identify the slow operation inside the handler.
**Fix:** Scale consumer instances. Make slow operations async. Batch process where possible. Optimize the bottleneck operation.

### Pattern: Duplicate messages causing duplicate processing
**Symptom:** Same message processed twice. Downstream effects happen twice.
**Why:** At-least-once delivery semantics. Consumer crashed after processing but before ACK. Network issue caused producer to retry.
**Prove:** Log message ID at processing start. Look for same ID appearing twice.
**Fix:** Implement idempotent consumers — this is the general fix and is required regardless of broker features. Kafka transactions (`isolation.level=read_committed` + transactional producer) give exactly-once semantics only for Kafka-internal read-process-write pipelines (consume from topic A, produce to topic B, atomically). They do NOT make external side effects — a DB write, an email send, a third-party API call — exactly-once; those still need the idempotent-consumer pattern (store processed message IDs, dedupe on that key) regardless of Kafka transaction usage.

### Pattern: Message ordering violated
**Symptom:** Events processed out of sequence. State inconsistent.
**Why:** Multiple partitions / consumers processing same entity in parallel. Producer not setting partition key. Consumer concurrency breaking order.
**Prove:** Log message offset/sequence and processing timestamp. Is processing order matching publish order?
**Fix:** Use partition key = entity ID (all messages for same entity go to same partition). Ensure single consumer per partition.

### Pattern: DB write succeeds, event never published (the dual-write problem)
**Symptom:** A service commits a database write, then crashes, redeploys, or hits a network blip before publishing the corresponding event/message. The DB and the message stream permanently disagree — downstream consumers never learn about a change that definitely happened. No error is logged at the point of loss; the write itself succeeded.
**Why:** Writing to the database and publishing to the message broker are two separate network calls with no shared transaction. There is no atomic way to "commit this row AND publish this message" across two different systems. Whichever order they're called in, a crash between the two calls loses one side. This is distinct from the Saga pattern (Category 7) — Sagas coordinate multi-step business transactions across services; this is the more fundamental problem of a single service's write and its own notification falling out of sync.
**Prove:** Compare DB row count/last-modified for an entity against the corresponding published-event count over the same time window. A gap — more DB changes than events — confirms lost publishes. Check deploy/restart timestamps against the gap window; crashes during a deploy are the most common trigger.
**Fix — Transactional Outbox pattern:** write the event to an `outbox` table in the SAME database transaction as the business write (this is atomic — it's one transaction, one database), then a separate relay process/CDC tool (Debezium, or a simple polling worker) reads the outbox table and publishes to the broker, marking rows as sent:
```sql
BEGIN;
  UPDATE orders SET status = 'paid' WHERE id = $1;
  INSERT INTO outbox (aggregate_id, event_type, payload, created_at)
  VALUES ($1, 'OrderPaid', $2, now());
COMMIT;
-- A relay process polls `outbox WHERE published_at IS NULL`, publishes to the
-- broker, then marks published_at. If the relay crashes after publish but
-- before marking, the event may publish twice — downstream consumers must
-- still be idempotent (Category 2's duplicate-message pattern applies).
```
**Do NOT:** try to solve this with a longer transaction that includes the broker publish — most message brokers are not transactional participants with your RDBMS, and even where XA/2PC is technically possible it is operationally fragile and rarely worth the complexity compared to the outbox pattern.

---

## CATEGORY 3 — MICROSERVICE COMMUNICATION

### Pattern: gRPC call hangs or fails under load — no deadline propagated
**Symptom:** A chain of gRPC service calls (A → B → C) occasionally hangs for a long time, or fails with `DEADLINE_EXCEEDED` or `UNAVAILABLE` only under load or when one downstream service is slow. Individual services look healthy in isolation.
**Why:** Each gRPC call in the chain was given its own independent timeout/deadline instead of propagating the REMAINING deadline from the incoming call. Service A gives itself 10s, calls B with a fresh 10s deadline, which calls C with another fresh 10s deadline — the caller-facing operation can now take up to 30s even though the caller only waited 10s before giving up, and A's own client-side timeout fires while B and C keep working on an already-abandoned request (wasted work, connection/thread pool pressure under load).
**Prove:** Log the deadline/remaining-time at the entry of each service in the chain. If each service logs a fresh full timeout instead of a shrinking remaining budget, deadlines are not being propagated. `UNAVAILABLE` appearing at A while B/C show no error at all is a signature of A's own timeout firing before B/C responded — not a real B/C failure.
**Fix:** Propagate the caller's remaining deadline through the whole call chain instead of giving every hop a fresh timeout:
```go
// Go — derive downstream context from the incoming context's deadline,
// don't create an independent timeout at each hop
func (s *serviceA) Handle(ctx context.Context, req *pb.Request) (*pb.Response, error) {
    // ctx already carries the caller's deadline — pass it straight through
    return s.bClient.Call(ctx, req) // NOT context.WithTimeout(context.Background(), 10*time.Second)
}
```
**Do NOT:** give each service a longer local timeout "to be safe" — that makes the problem worse (more wasted work on requests the original caller already gave up on) rather than fixing propagation.

### Pattern: Service call succeeds, data wrong or missing
**Symptom:** HTTP 200 from downstream service. Response body doesn't match expected contract.
**Why:** Contract drift — downstream service updated its response schema. Wrong service version called. Serialization difference (camelCase vs snake_case). Default values changed.
**Prove:** Log the raw response body from the downstream service. Compare to expected schema.
**Fix:** Version your APIs. Use contract testing. Validate response schema explicitly. Log schema version in responses.

### Pattern: Cascading failure — one service down takes others down
**Symptom:** Service A fails. Services B, C, D all fail because they depend on A.
**Why:** No timeout on calls to Service A. No circuit breaker. Threads/connections blocked waiting. Resource pool exhausted.
**Prove:** Simulate Service A being slow (not down — slow). Does everything else slow down too?
**Fix:** Set timeouts on ALL inter-service calls. Implement circuit breaker pattern. Return fallback/cached response when downstream fails. Use bulkhead pattern.

### Pattern: Service discovery failure — correct service not found
**Symptom:** Service registered. Other service can't find it or calls wrong instance.
**Why:** Service registered on wrong host/port. Health check failing (service deregistered). DNS cache stale. Wrong service name in registry.
**Prove:** Query service registry directly. Is the service registered? With correct host/port? Is it healthy?
**Fix:** Fix health check endpoint. Verify service registration at startup. Reduce DNS TTL. Log the resolved address before every call.

### Pattern: Distributed tracing shows orphaned spans
**Symptom:** Some requests show complete traces. Others are missing spans or have broken parent-child links.
**Why:** Trace context not propagated across service boundary. Missing `traceparent` header forwarding. Async operations losing context. SDK not initialized.
**Prove:** Log the trace ID at entry of each service. Check if same trace ID appears across services.
**Fix:** Forward trace context headers explicitly on every inter-service call. Initialize tracing SDK before any code. Use async context propagation.

---

## CATEGORY 4 — DATA PIPELINES & ETL

### Pattern: ETL runs successfully, rows missing in destination
**Symptom:** Extract: 10,000 rows. Load: 8,500 rows. No error. 1,500 rows silently dropped.
**Why:** Transform step silently filtering rows (null check, validation). Load step ignoring insert errors (ON CONFLICT DO NOTHING). Batch size issue — last batch not flushed.
**Prove:** Count rows at EVERY stage: after extract, after transform, after load. Find the stage where count drops.
**Fix:** Log row count at each stage. Never silently drop rows — log them to a rejection table with reason. Flush all batches explicitly. Validate count before marking pipeline complete.

### Pattern: Data transformation produces wrong values
**Symptom:** Pipeline runs. Destination has data. Values are wrong (truncated, rounded, wrong format).
**Why:** Type conversion losing precision. String truncation at column width. Timezone conversion wrong. Null coalesced to wrong default.
**Prove:** Run transformation on a small known sample. Compare input vs output for each column.
**Fix:** Test transform logic on edge cases: nulls, empty strings, max values, special characters, different timezones. Add data quality checks after transform.

### Pattern: Pipeline fails on day 1 of month / year boundary
**Symptom:** Pipeline works for weeks. Fails on January 1st, first of month, or midnight.
**Why:** Date arithmetic crossing month/year boundary. Off-by-one in date range. Partition key changes. Log rotation coinciding. Report period calculation wrong.
**Prove:** Run pipeline with a date set to boundary date (month-end, year-end, midnight).
**Fix:** Use explicit date range calculations. Test with boundary dates. Never assume "yesterday" logic works at boundaries.

### Pattern: Incremental pipeline reprocessing old data
**Symptom:** Pipeline should only process new records. Processing everything again. Duplicate data in destination.
**Why:** Watermark/checkpoint not saved correctly. Checkpoint not loaded at startup. Wrong column used for incremental filtering. Timestamp precision mismatch.
**Prove:** Log the watermark value at pipeline start and end. Is it being loaded and saved correctly?
**Fix:** Persist checkpoint atomically after successful load. Log checkpoint values. Use high-watermark column with correct data type and precision.

### Pattern: Schema change breaks pipeline
**Symptom:** Pipeline worked. Source schema changed. Pipeline fails or silently produces wrong data.
**Why:** Column added/removed/renamed in source. Type changed. New required column with no default.
**Prove:** Compare source schema now vs when pipeline was written. What changed?
**Fix:** Add schema validation at extract stage. Alert on schema change. Make pipeline resilient to additive changes (new columns). Fail loudly on breaking changes.

---

## CATEGORY 5 — CI/CD PIPELINES

### Pattern: Pipeline passes, deployed app broken
**Symptom:** All CI checks green. Deploy succeeds. App behaves incorrectly in production.
**Why:** Tests not covering the broken scenario. Tests running against mocks/stubs not real dependencies. Different config/env between CI and prod. DB migration not run.
**Prove:** Run the same tests against production environment (smoke test). Which test would have caught this?
**Fix:** Add post-deploy smoke tests. Run integration tests against real dependencies in CI. Validate migrations run as part of deploy. Diff CI env vs prod env.

### Pattern: Build succeeds on developer machine, fails in CI
**Symptom:** Local build passes. Same code fails in CI pipeline.
**Why:** Different OS/platform (macOS vs Linux line endings, case sensitivity). Missing environment variable. Different dependency version (no lock file). Test relying on local file not in repo.
**Prove:** Run `env` in CI to see environment. Compare to local. Check CI OS vs local OS.
**Fix:** Commit lock files. Containerize build (Docker). Set all required env vars in CI config. Check for case-sensitive file paths.

### Pattern: Deployment succeeds but old version still running
**Symptom:** Deploy pipeline completes. New features not visible. Logs show old version.
**Why:** Blue-green: traffic not switched. Container image cached — pulling old image. Multiple instances — only some updated. CDN caching old assets. Service not restarted.
**Prove:** Hit a `/health` or `/version` endpoint that returns the deployed commit SHA or version string. If it returns the old value after deploy → old code is running. No such endpoint? Add `log.info("App version: {}", System.getenv("GIT_SHA"))` at startup — compare against the commit deployed. For containers: `docker inspect <container> | grep Image` — confirm image digest matches the newly built image.
**Fix:** Add version endpoint to app. After deploy, verify version endpoint returns new version. Force image pull in deploy config. Invalidate CDN cache. Verify all instances updated.

### Pattern: Environment variables missing in deployed environment
**Symptom:** App works in CI. Fails in deployed environment with "configuration missing" or similar.
**Why:** Env var set in CI secrets but not in deploy target's secret manager. New variable added locally, not added to CI/CD config.
**Prove:** Print all expected env vars at app startup (redact values). Which ones are undefined?
**Fix:** Maintain a documented list of required env vars. Validate all required vars at startup — fail fast with clear error. Add to CI/CD config AND deploy target secret manager together.

### Pattern: Database migration runs in wrong order
**Symptom:** Migration runs. App crashes. Schema in unexpected state.
**Why:** Migrations not applied in correct sequence. Out-of-order migration file. Migration applied partially then failed. Schema diverged between environments.
**Prove:** Compare actual schema to expected schema after migration. Check migration history table.
**Fix:** Use sequential migration numbers. Never edit existing migrations — always add new ones. Lock migration table during apply. Run migration validation after apply.

---

## CATEGORY 6 — API GATEWAY & SERVICE MESH

### Pattern: Request succeeds at gateway, fails at service
**Symptom:** Gateway returns response. Service logs show no request received.
**Why:** Gateway caching the response. Gateway short-circuiting (rate limit, circuit breaker). Request transformation stripping required headers. Routing to wrong backend.
**Prove:** Check gateway access logs AND service access logs. Does the request appear in both?
**Fix:** Disable gateway cache for debugging. Log request at gateway entry and service entry. Compare headers at both points.

### Pattern: Headers stripped between gateway and service
**Symptom:** Client sends headers. Service doesn't receive them.
**Why:** Gateway not forwarding custom headers. Hop-by-hop headers stripped. Header name case mismatch. Authentication header transformed.
**Prove:** Log all headers at service entry. Which headers from client are missing?
**Fix:** Configure gateway to forward specific headers. Use standard header names. Log header transformation at gateway.

### Pattern: mTLS/service mesh causing connection failures
**Symptom:** Services worked before mesh. After mesh setup, service-to-service calls fail.
**Why:** Certificate not issued for service. Sidecar not injected. mTLS policy requiring cert but service doesn't have one. Certificate expired.
**Prove:** Check sidecar injection status. Check certificate validity. Try call with mTLS disabled (test only).
**Fix:** Ensure sidecar injected in all namespaces. Rotate expired certificates. Configure mTLS policy correctly for all services.

---

## CATEGORY 7 — DATA CONSISTENCY & EVENTUAL CONSISTENCY

### Pattern: Read-after-write inconsistency
**Symptom:** User saves data. Immediately reads it back. Gets old data.
**Why:** Write went to primary. Read routed to replica. Replication lag. Cache not invalidated.
**Prove:** Read directly from primary immediately after write. If correct → replica lag confirmed.
**Fix:** Route reads to primary for critical read-after-write scenarios. Or use write-through cache. Or implement read-your-writes consistency.

### Pattern: Saga/distributed transaction partially completed
**Symptom:** Multi-step operation. Step 3 fails. Steps 1 and 2 already committed. Data inconsistent.
**Why:** No compensating transactions. No saga orchestration. Failure handling not implemented.
**Prove:** Force failure at each step. Check state of all services after each failure.
**Fix:** Implement saga pattern with compensating transactions. Use saga orchestrator or choreography with proper rollback. Implement idempotent compensating actions.

### Pattern: Event sourcing replay produces different state
**Symptom:** Replaying event log produces different final state than live system.
**Why:** Non-deterministic logic in event handler (current time, random, external state). Event handler logic changed after events were stored. Events missing from log.
**Prove:** Replay with fixed timestamp. Does it match? If yes → non-determinism is the cause.
**Fix:** Event handlers must be pure functions of the event only. Never use current time or external state. Version event handler logic with event schema version.

---

## CATEGORY 8 — KUBERNETES HEALTH PROBE SEMANTICS

### Pattern: Pod marked ready but requests fail — probe checks HTTP not actual dependencies

**Symptom:** Pod is `1/1 READY`. Requests fail with connection errors or 5xx immediately after startup, or for 20-30 seconds until dependencies warm up. Restarting the pod temporarily fixes sustained failures. The readiness probe always returns 200.
**Why:** The readiness endpoint only verifies the HTTP server is listening — no dependency checks. Kubernetes marks the pod ready based on this alone. Redis, PostgreSQL, or other dependencies may not be connected yet.
**Prove:** While requests are failing: `kubectl exec -it <pod> -- curl -s localhost:<port>/health/ready`. Returns 200 → the probe is lying. Check the handler — if it has no `ping()` or `SELECT 1`, it is not checking real dependencies.
**Fix:** The readiness endpoint must verify every dependency needed to serve requests:
```js
// Node.js / Express — adapt to your ORM/driver
app.get('/health/ready', async (req, res) => {
  try {
    await redis.ping()                    // not just 'redis client exists'
    await db.query('SELECT 1')           // not just 'db object initialized'
    // Prisma: await db.$queryRaw`SELECT 1`
    // Mongoose: await mongoose.connection.db.admin().ping()
    res.json({ ready: true })
  } catch (err) {
    res.status(503).json({ ready: false, error: err.message })
  }
})
```
```python
# FastAPI / Python
@app.get("/health/ready")
async def readiness():
    try:
        await redis_client.ping()
        await db.execute("SELECT 1")
    except Exception as e:
        return JSONResponse(status_code=503, content={"ready": False, "error": str(e)})
    return {"ready": True}
```
**Key rule:** `/health/live` (liveness) = "is the process alive?" — 200 if event loop running. `/health/ready` (readiness) = "can this pod serve real traffic?" — only 200 when ALL dependencies respond. Never use the same endpoint for both.

**Caveat — don't overcorrect into a correlated-failure outage:** if the readiness check pings a *shared* dependency (a Redis/Postgres instance used by every pod in the deployment) and that dependency has a transient blip, every pod fails readiness **simultaneously**. Kubernetes then pulls the entire Service's endpoints, and a brief, partial backend issue becomes a total outage — even for request paths that don't touch that dependency, or that could be served in a degraded mode. For dependencies shared across the whole deployment, consider: checking only per-instance-critical dependencies in readiness (not every shared dependency), a short grace period / failure-count threshold before flipping to not-ready, or explicitly serving degraded responses instead of failing readiness outright.

### Pattern: Kubernetes pod never becomes ready (readiness probe misconfigured)

**Symptom:** Pod stuck in `0/1 READY`. `kubectl describe pod` shows readiness probe failing.
**Why:** Probe path wrong, port wrong, initialDelaySeconds too short, or app genuinely failing.
**Prove:** `kubectl exec -it <pod> -- curl localhost:<port>/health/ready` — does it return 200 from inside the pod?
**Fix:** Fix the probe path/port, increase initialDelaySeconds, or fix the health endpoint.
