# Universal Bug Patterns Reference

Stack-agnostic. Any language, framework, or platform.
Each pattern: symptom → why → how to prove → how to fix.

---

## CATEGORY 1 — ASYNC & CONCURRENCY

### Pattern: Result used before operation completes
**Symptom:** Value is null/empty/default even though you "set it"
**Why:** Async operation not awaited. Callback not yet complete.
**Prove:** Log timestamp after trigger AND when result is used. Same timestamp = not awaited.
**Fix:** Await the operation. Move result usage inside the callback/then/after.

### Pattern: Race condition on shared state
**Symptom:** Works 80% of the time. Fails randomly or only under load.
**Why:** Two concurrent operations read-modify-write the same value.
**Prove:** Assign unique ID to each operation. Log start+end with ID. Look for interleaving in logs.
**Fix:** Mutex / lock / atomic operation / serialize via queue.

### Pattern: Stale closure / captured variable
**Symptom:** Callback uses old value despite the variable being updated outside.
**Why:** Closure captured the variable AT CREATION TIME, not execution time.
**Prove:** Log the value INSIDE the callback and OUTSIDE it. They will differ.
**Fix:** Pass value as explicit parameter into callback. Avoid capturing mutable outer vars.

### Pattern: Deadlock — two locks acquired in opposite order
**Symptom:** Process hangs forever under certain conditions. Never crashes, never continues.
**Why:** Thread A holds Lock1, waits for Lock2. Thread B holds Lock2, waits for Lock1.
**Prove:** Thread dump / stack trace shows both threads in WAITING state.
**Fix:** Always acquire locks in the same order everywhere. Or use a single lock. Or use lock-free structure.

### Pattern: Promise/future not properly chained
**Symptom:** Error from async op silently disappears. Nothing breaks, nothing succeeds.
**Why:** Promise rejected but `.catch()` missing or returns without propagating.
**Prove:** Add `.catch(err => console.error('UNHANDLED:', err))` at the end of every chain.
**Fix:** Always handle rejections. Always return promises from async functions.

---

## CATEGORY 2 — STATE & MUTATION

### Pattern: Mutating a copy instead of original
**Symptom:** Update runs without error. Original object unchanged.
**Why:** Assignment created shallow copy. Mutation happened on the copy, not the source.
**Prove:** Log object identity (id(obj) in Python / reference equality in JS) before and after.
**Fix:** Mutate in place. Or explicitly replace the original reference. Know your language's copy semantics.

### Pattern: Shared mutable default argument
**Symptom:** State bleeds between calls. First call fine, subsequent calls get contaminated data.
**Why:** Mutable default (list, dict, object) shared across all calls in Python and similar.
**Prove:** Call the function twice with no arguments. Compare results. If different → shared state.
**Fix:** Use `None` as default, initialize inside the function body.

### Pattern: Event not reaching handler
**Symptom:** Event fires (confirmed by log), handler never executes.
**Why:** Wrong event name string. Listener on wrong object/scope. Registered AFTER event fired.
**Prove:** First line of handler = log. If never prints → handler not reached.
**Fix:** Verify exact string match of event name. Verify registration order. Verify correct object.

### Pattern: Reactive framework state bypass
**Symptom:** DOM/UI updates visually but internal model unchanged. Validation still fails.
**Why:** State mutated directly instead of through framework's setter/reducer/signal.
**Prove:** Read state from framework's own API after mutation. Compare to DOM.
**Fix:** Only mutate state through the framework's prescribed method. Never mutate backing object directly.

---

## CATEGORY 3 — DATA, TYPES & FORMATS

### Pattern: Type coercion silent mismatch
**Symptom:** Comparison always false. Value never found in collection. Filter returns nothing.
**Why:** "1" !== 1. null !== undefined. 0 !== false. Implicit coercion changed the type.
**Prove:** Log `typeof x` and `typeof y` on both sides of the comparison.
**Fix:** Explicit conversion before comparison. Use strict equality (=== not ==).

### Pattern: Integer overflow / precision loss
**Symptom:** Large numbers produce wrong results. Financial calculations off by small amounts.
**Why:** Integer overflow wraps around. Float loses precision (0.1 + 0.2 ≠ 0.3).
**Prove:** Print the raw value right before the operation. Check if it exceeds type's max.
**Fix:** Use BigInt / BigDecimal / arbitrary precision library. Never use float for money.

### Pattern: Date format mismatch at boundary
**Symptom:** Value passes through code correctly. External system rejects it or misinterprets it.
**Why:** DD/MM vs MM/DD. Timezone offset missing. ISO vs locale format. Unix timestamp vs ms.
**Prove:** Log the EXACT string being sent. Compare character by character with what system expects.
**Fix:** Explicit format conversion at EVERY system boundary. Never trust implicit conversion.

### Pattern: Timezone bug — correct time, wrong zone
**Symptom:** Date/time correct in dev, off by hours in prod. Crosses midnight in one TZ, not another.
**Why:** Server in UTC, client in IST (+5:30). Dates stored without TZ. Comparison crosses midnight.
**Prove:** Log timezone of system at runtime. Log UTC value AND local value of every date.
**Fix:** Store all dates in UTC. Convert to local timezone ONLY at display layer. Never assume TZ.

### Pattern: Encoding mismatch
**Symptom:** String looks correct in logs. Breaks downstream. Special characters cause errors.
**Why:** UTF-8 vs Latin-1. URL encoding missing. Base64 padding wrong. BOM character hidden.
**Prove:** Log BYTE representation, not string representation. `repr(x)` in Python. `Buffer.from(x)` in JS.
**Fix:** Explicit encode/decode at every I/O boundary. Set encoding explicitly, never assume.

### Pattern: Null / empty / zero not guarded
**Symptom:** Code runs without error. Wrong output for edge inputs. Works for typical data only.
**Why:** No guard for null/empty/0/[]/{}. Default value used silently. NullPointerException hidden.
**Prove:** Test with null, "", 0, [], {} as inputs. Log what the function actually receives.
**Fix:** Explicit guard clauses at function entry. Validate before operating, not after.

### Pattern: Serialization of special types
**Symptom:** Object serialized and deserialized but comes back wrong type or missing fields.
**Why:** Custom object, Date, Decimal, Set, Map serialized to JSON loses type info.
**Prove:** Serialize then deserialize immediately. Log type of each field before and after.
**Fix:** Custom serializer/deserializer for special types. Validate round-trip in tests.

---

## CATEGORY 4 — NETWORK & API

### Pattern: Silent 2xx with error in body
**Symptom:** API call "succeeds" (no exception thrown). Nothing changes. No visible error.
**Why:** Server returns 200 with `{"success": false, "error": "..."}` in body. Client checks only status code.
**Prove:** Log the FULL response body, not just status code.
**Fix:** Parse response body. Check semantic success field. Throw on business-logic failure.

### Pattern: Wrong endpoint called
**Symptom:** Request fires. Server processes something. Result wrong or missing.
**Why:** URL constructed incorrectly. Base URL different per env. Trailing slash mismatch. Typo.
**Prove:** Log the fully-resolved URL string being called before every request.
**Fix:** Construct URL explicitly. Log it. Verify it. Never concatenate without logging.

### Pattern: Payload not sent as expected
**Symptom:** Server receives request but acts on empty/wrong data.
**Why:** Wrong Content-Type header. Serialization issue. Nested vs flat structure mismatch.
**Prove:** Log the exact serialized body string before sending. Check Content-Type header.
**Fix:** Verify Content-Type matches payload format. Log and inspect outgoing body.

### Pattern: Retry hiding the real error
**Symptom:** Code retries silently. Eventually "succeeds" — but returns wrong data. Or always fails after retries with vague error.
**Why:** Retry swallows intermediate errors. Last retry error masks root cause.
**Prove:** Log EVERY attempt, EVERY error, with full detail. Disable retries temporarily.
**Fix:** Log all errors during retry. Surface root error, not "max retries exceeded."

### Pattern: Connection timeout vs connection refused
**Symptom:** Network error on external call. Generic "connection failed."
**Why:** Timeout = service reachable but slow/hung. Refused = service not listening. Different fixes.
**Prove:** Check error code. ETIMEDOUT vs ECONNREFUSED. Try `curl -v` directly.
**Fix:** Timeout → increase timeout or fix slow service. Refused → fix host/port/firewall/service not running.

### Pattern: SSL/TLS certificate error swallowed
**Symptom:** HTTPS call fails silently. Works with `verify=False` / `rejectUnauthorized: false`.
**Why:** Cert expired. Self-signed in prod. Wrong hostname. Missing intermediate cert.
**Prove:** Enable verbose SSL logging. Run `openssl s_client -connect host:443`.
**Fix:** Fix the certificate. Never disable verification in prod — it hides the real problem.

---

## CATEGORY 5 — ENVIRONMENT & CONFIG

### Pattern: Wrong environment variable
**Symptom:** Works locally, fails in staging/prod. Credentials wrong. URLs wrong. Behavior different.
**Why:** .env not loaded. Wrong .env file. OS env var overrides app config. Variable name typo.
**Prove:** Print ALL env vars the app reads at startup. Compare local vs prod explicitly.
**Fix:** Validate required env vars at startup. Fail fast with clear error if missing or wrong.

### Pattern: Wrong dependency version
**Symptom:** Feature works in dev, breaks in prod. Breaks after deploy. Works on one machine, not another.
**Why:** Different package versions. Unpinned dependency updated. Cached old build artifact.
**Prove:** Log the actual dependency version at runtime. Compare local vs prod.
**Fix:** Pin all dependency versions. Lock file committed. Clean install in CI. Verify runtime version.

### Pattern: Wrong code deployed
**Symptom:** Fix applied, bug persists. Logs show impossible behavior. Obvious fix has no effect.
**Why:** Old build running. Container not rebuilt. Cache not cleared. Wrong branch deployed. Multiple instances, only some updated.
**Prove:** Add unique sentinel log immediately in the fixed code. If log never appears → old code running.
**Fix:** Rebuild. Restart. Clear cache. Verify ALL instances updated. Confirm sentinel log appears.

### Pattern: File path resolves differently across environments
**Symptom:** Config/asset/script not found in prod. Works locally. FileNotFoundError in prod only.
**Why:** Relative path resolves from different working directory. Symlink not followed in container.
**Prove:** Log the absolute resolved path at runtime. `os.path.abspath()` / `path.resolve()`.
**Fix:** Use absolute paths anchored to script's own directory. Never assume working directory.

### Pattern: Log level hiding errors
**Symptom:** No errors in logs. Bug is real and reproducible. Logs seem clean.
**Why:** Logger set to INFO or WARN. Error logged at DEBUG level. Never appears in output.
**Prove:** Temporarily set log level to DEBUG/TRACE. Run again. Look for hidden errors.
**Fix:** Log errors at ERROR level always. Set DEBUG log level in dev. Fix log level config.

---

## CATEGORY 6 — DATABASE & CACHING

### Pattern: Read from stale cache
**Symptom:** Write succeeds. Immediate read returns old value. Direct DB query returns correct value.
**Why:** Cache not invalidated after write. TTL not expired. Read hitting cache layer, not DB.
**Prove:** Bypass cache entirely. Query DB directly. If DB has correct value → cache is stale.
**Fix:** Invalidate or update cache on write. Reduce TTL for debug. Use cache-aside pattern correctly.

### Pattern: Transaction not committed
**Symptom:** Write in one session not visible in another. Data appears after some delay or not at all.
**Why:** Transaction open but not committed. Rolled back silently. Reading before commit.
**Prove:** Check open transactions. Query `pg_stat_activity` (Postgres) or equivalent.
**Fix:** Commit explicitly. Verify no silent rollback. Check autocommit setting.

### Pattern: Reading from replica (replication lag)
**Symptom:** Write succeeds, immediate read returns old/missing data. Works consistently after delay.
**Why:** Read routed to replica. Replica lag = data not yet synced from primary.
**Prove:** Run same read query directly on primary. If it returns correct → replica lag confirmed.
**Fix:** Route post-write reads to primary. Or add delay before read. Or use read-your-writes routing.

### Pattern: N+1 query causing timeout / wrong results
**Symptom:** Works for small data, slow or broken for large data. Behavior changes with data volume.
**Why:** Query inside loop. 1 query becomes N queries for N records. DB overwhelmed or times out.
**Prove:** Log count of DB calls. Add query counter. Should be constant, not proportional to data size.
**Fix:** Batch query outside loop. Use JOIN. Use `IN (...)`. Fetch all needed data in one query.

### Pattern: Deadlock on DB rows
**Symptom:** Transaction randomly fails with "deadlock detected." Works in low traffic, breaks under load.
**Why:** Two transactions updating the same rows in opposite order.
**Prove:** Check DB deadlock logs. They show exactly which transactions and rows are involved.
**Fix:** Update rows in consistent order across all transactions. Or use SELECT FOR UPDATE to pre-lock.

---

## CATEGORY 7 — INTERCEPTION LAYERS

### Pattern: Middleware absorbing request silently
**Symptom:** Call made, handler never executes. No error. Complete silence.
**Why:** Auth middleware rejecting. Rate limiter dropping. CORS preflight failing. Router not matching.
**Prove:** Put a log as absolute FIRST line of the handler. Not reached → something upstream intercepted.
**Fix:** Work backwards from handler. Check each layer: auth → rate limit → CORS → routing → middleware.

### Pattern: Decorator / wrapper modifying return value
**Symptom:** Function returns correct value. Caller receives different value. No error thrown.
**Why:** Decorator transforms output. Wrapper caches stale result. AOP interceptor modifying.
**Prove:** Log return value INSIDE the function AND at the call site. If different → layer in between.
**Fix:** Identify the decorator/wrapper. Inspect its transformation. Fix or bypass for this case.

### Pattern: Error swallowed in try/catch
**Symptom:** No error in logs. Bug is real. Code path reached. Silent failure.
**Why:** `catch(e) {}` or `catch(e) { return null }` — error caught, nothing done with it.
**Prove:** Search codebase for empty catch blocks and catches that don't re-throw or log.
**Fix:** Log ALL caught errors. Re-throw if not recoverable. Never swallow silently.

---

## CATEGORY 8 — BUILD, DEPLOY & HOT RELOAD

### Pattern: Hot reload not picking up changes
**Symptom:** Code changed. Process not restarted. Old behavior persists. No error.
**Why:** Hot reload only re-runs changed module. Other modules cached. State from old version persists.
**Prove:** Full restart (not hot reload). If bug disappears → hot reload was serving stale code.
**Fix:** Full restart when changing core modules. Do not rely on hot reload for debugging.

### Pattern: Test mock bleeding into production code path
**Symptom:** Tests pass. Production fails. Or production behavior changes depending on test order.
**Why:** Mock not properly scoped. Global mock leaks between tests. Module import cached with mock.
**Prove:** Run production code path in isolation with no test framework loaded. Does it still work?
**Fix:** Scope mocks to test only. Restore originals in teardown. Use dependency injection instead.

### Pattern: Two bugs masking each other
**Symptom:** Fix applied, different bug appears. Or: fix one place, breaks another.
**Why:** Bug A was compensating for Bug B. Fixing A reveals B. Or: two independent bugs co-existing.
**Prove:** Revert fix. Original symptom returns. Apply fix. New symptom appears. → Two bugs confirmed.
**Fix:** Treat them as separate bugs. Run Phase 3 fresh on the new symptom. Do not conflate.

---

## CATEGORY 9 — MEMORY & RESOURCES

### Pattern: Memory leak → eventual crash or slowdown
**Symptom:** Works initially. Degrades over time. Crashes after hours/days. Memory grows unbounded.
**Why:** Objects allocated, never released. Event listeners never removed. Circular references.
**Prove:** Log memory usage at regular intervals. Look for monotonic growth. Heap dump analysis.
**Fix:** Remove listeners on cleanup. Clear caches with TTL. Use weak references where appropriate.

### Pattern: Connection pool exhaustion
**Symptom:** Works under low load. Hangs or crashes under concurrent usage. "No connections available."
**Why:** Connections acquired but not released. Pool size too small for load. Leak in error path.
**Prove:** Log pool size and active connections before each acquire. Look for monotonic growth.
**Fix:** Always release connections in finally/defer. Size pool to match expected concurrency. Fix leak in error path.

### Pattern: File descriptor exhaustion
**Symptom:** "Too many open files" error. Works initially, fails after sustained operation.
**Why:** Files/sockets opened but never closed. Error path skips close.
**Prove:** Log open file count (`/proc/self/fd` on Linux). Watch it grow.
**Fix:** Use context managers / try-with-resources / defer. Always close in finally block.

---

## CATEGORY 10 — LOGIC & ALGORITHM EDGE CASES

### Pattern: Off-by-one
**Symptom:** Works for typical cases. Wrong for first item, last item, or empty collection.
**Why:** `<` vs `<=`. 0-indexed vs 1-indexed. Fence-post error. Page boundary error.
**Prove:** Test with: empty input, single item, exactly-at-boundary input.
**Fix:** Draw out the boundary explicitly. Use inclusive/exclusive ranges consistently.

### Pattern: Greedy regex consuming too much
**Symptom:** Regex works on simple input. Returns wrong match on complex input.
**Why:** `.*` is greedy — matches as much as possible. Captures beyond intended boundary.
**Prove:** Test regex on the exact failing input in isolation (regex101.com or similar).
**Fix:** Use non-greedy `.*?`. Or use specific character classes instead of `.`.

### Pattern: Incorrect boolean logic
**Symptom:** Condition seems right. Wrong branch executes. Fails for specific combinations of inputs.
**Why:** AND vs OR confusion. Double negative. Operator precedence. De Morgan's law violated.
**Prove:** Log the value of each sub-condition independently before the compound condition.
**Fix:** Break compound condition into named variables. Log each. Simplify using De Morgan's laws.

### Pattern: Mutation during iteration
**Symptom:** Loop produces unexpected results. Skips items. Infinite loop. ConcurrentModificationException.
**Why:** Collection modified while being iterated over.
**Prove:** Log collection size at start of loop and on each iteration. Should be constant.
**Fix:** Iterate over a copy. Collect mutations and apply after loop completes.
