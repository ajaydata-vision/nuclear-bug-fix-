# Evaluator

## Metadata

- id: JV-008
- domain: java-enterprise
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: threadlocal, mdc, slf4j, filter, spring-boot, thread-pool, security

## Ground Truth

- root_cause: MDC.put("userId", userId) is called but MDC.clear() (or MDC.remove("userId")) is never called after the request completes. MDC is backed by a ThreadLocal. Tomcat's thread pool reuses threads across requests. The previous request's MDC values survive into the next request on the same thread.
- why_it_happens: ThreadLocal values persist on a thread indefinitely until explicitly removed. Thread pool threads are reused without cleanup between tasks unless the task cleans up after itself. MDC.clear() must be called in a finally block to guarantee cleanup regardless of exceptions.
- accepted_fix: Add MDC.clear() in a finally block after chain.doFilter():
  try { MDC.put("userId", userId); chain.doFilter(req, res); } finally { MDC.clear(); }
- rejected_fix_patterns:
  - call MDC.clear() after chain.doFilter() but not in finally (skipped on exception)
  - use a new thread per request (defeats thread pool purpose)

## Evidence Signals

- strongest_signal: Same thread name (exec-3) appears in logs for different users sequentially; MDC.clear() absent from filter code; MDC is ThreadLocal-backed
- strongest_alternative_explanation: Race condition in userId extraction logic reading wrong session
- why_alternative_is_wrong: The log shows correct userId on first request for exec-3, then wrong userId on subsequent request — the session extraction works correctly (security checks pass); the issue is the previous MDC value persisting on thread reuse

## Scoring Notes

- full_credit_conditions:
  - identifies missing MDC.clear() in finally block as root cause
  - explains ThreadLocal persistence across thread pool reuse
  - proposes try/finally with MDC.clear() or MDC.remove()
- partial_credit_conditions:
  - identifies MDC leak but proposes MDC.clear() outside finally block
- fail_conditions:
  - suggests the session management is broken
  - recommends disabling thread pooling
