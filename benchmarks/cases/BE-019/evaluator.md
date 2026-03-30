# Evaluator

## Metadata

- id: BE-019
- domain: backend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: cache, redis, invalidation, stale-read, write-through

## Ground Truth

- root_cause: The cache entry is not invalidated on update, so the stale cached value is served until the TTL expires.
- why_it_happens: Read-through caching must be paired with cache invalidation on writes. Without explicit deletion or update of the cache entry, reads return the cached value regardless of database changes.
- accepted_fix: Delete the cache key after a successful update: await redis.del(`product:${id}`) in updateProduct.
- rejected_fix_patterns:
  - reduce TTL to 1 second
  - add a random jitter to TTL

## Evidence Signals

- strongest_signal: Stale data served exactly until TTL; correct data immediately after del in cache
- strongest_alternative_explanation: Database write failing silently
- why_alternative_is_wrong: Correct data is visible after TTL expiry proving the DB write succeeded; the issue is cache not invalidated

## Scoring Notes

- full_credit_conditions:
  - identifies missing cache invalidation on update
  - proposes redis.del on update
  - explains read-through + invalidation pattern
- partial_credit_conditions:
  - identifies cache issue but proposes only reducing TTL
- fail_conditions:
  - suggests disabling caching entirely
  - adds cache-control headers (wrong layer)
