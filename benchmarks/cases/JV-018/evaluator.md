# Evaluator

## Metadata

- id: JV-018
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: spring-boot, cache, cacheable, cacheevict, redis, spel, key-mismatch

## Ground Truth

- root_cause: `@Cacheable` uses `key = "#userId"` where `userId` is `Long`. `@CacheEvict` uses `key = "#user.id"` where `UserProfile.getId()` returns `Integer`. Spring Cache uses the key object's type in serialisation — a `Long` 42L and an `Integer` 42 produce different Redis key strings (`users::42` from Long vs `users::42` from Integer may differ depending on the Redis serialiser, but more fundamentally `SimpleKeyGenerator` treats `Long(42)` and `Integer(42)` as unequal objects). The eviction targets a key that was never stored, leaving the original cached entry intact.
- why_it_happens: Spring Cache computes the cache key from the SpEL expression's resolved value, including its Java type. `#userId` resolves to `Long(42)`. `#user.id` resolves to `Integer(42)` because `UserProfile.getId()` returns `Integer`. Even though both print as "42", they are different objects and may serialise to different Redis key representations. The eviction command succeeds (no error) but deletes a key that was never written, while `users::42` (stored by the Long-keyed @Cacheable) remains.
- accepted_fix: Align the key expressions so both target the exact same cache key. Option A: change `@CacheEvict` key to `#user.id` while ensuring `UserProfile.getId()` returns `Long` (matching `#userId` type). Option B: add a dedicated `evictUser(Long userId)` method with `key = "#userId"` and call it from `updateUser`. Option C: use `@CacheConfig(cacheNames = "users")` at class level and use consistent key expressions.
- rejected_fix_patterns:
  - call `cacheManager.getCache("users").clear()` (evicts all users, not just the updated one)
  - add `@CachePut` instead of `@CacheEvict` on the update method (would cache the update result, valid alternative but not a fix for the key mismatch root cause)
  - increase Redis TTL to work around stale data (masks the bug, does not fix it)

## Evidence Signals

- strongest_signal: Eviction log appears (`[CACHE] evicting user 42`) but `redis-cli KEYS users::*` shows `users::42` still present after eviction — the eviction targeted a different key than the one stored; `@Cacheable` uses `#userId` and `@CacheEvict` uses `#user.id` (different SpEL expressions for the same conceptual value)
- strongest_alternative_explanation: Redis is not connected and cache operations are silently failing, so both store and evict are no-ops
- why_alternative_is_wrong: The first GET produces a MISS log (`loading user 42 from DB`) and subsequent GETs produce no log — proving cache storage is working (HIT). If Redis were disconnected, every GET would be a MISS. The eviction log also appears, confirming the evict code executes. Only the KEYS output (key still present) reveals the eviction targeted the wrong key.

## Scoring Notes

- full_credit_conditions:
  - identifies SpEL key expression mismatch between `@Cacheable` (`#userId`) and `@CacheEvict` (`#user.id`) as root cause
  - explains that both resolve to the same integer value but may produce different cache keys due to type differences in serialisation
  - prescribes aligning the key expressions to use the same SpEL path
- partial_credit_conditions:
  - identifies a caching problem and prescribes `allEntries = true` on `@CacheEvict` (works but evicts all users — not targeted)
  - identifies the key mismatch but prescribes `@CachePut` instead of fixing `@CacheEvict` key
- fail_conditions:
  - blames Redis connectivity
  - recommends clearing the entire cache on every update
  - suggests increasing TTL as the fix
