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

- root_cause: The `@Cacheable` key expression is `#userId` (the method parameter — a `Long`) and the `@CacheEvict` key expression is `#user.id` (a field on the `UserProfile` object). Both resolve to the integer value `42`, but Spring Cache serialises the cache key differently depending on how the SpEL expression resolves. `#userId` resolves to a `Long` at the call site; `#user.id` resolves to whatever type `UserProfile.getId()` returns. If there is any type difference (e.g., `Long` vs `Integer`), or if the Redis key serialisation produces different strings, the eviction targets a different Redis key than the one the cacheable method stored.
- why_it_happens: The cache key used by `@Cacheable` is computed from `#userId` — the method parameter named `userId`. The key used by `@CacheEvict` is computed from `#user.id` — the `id` field of the passed-in `UserProfile` object. Even though both values equal `42` at runtime, Spring Cache resolves and serialises SpEL expressions independently. Using `#user.id` vs `#userId` introduces a fragile dependency on type consistency. The safest fix is to make both expressions identical: use `#userId` in `@Cacheable` and `#user.id` in `@CacheEvict`, OR unify them by having the update method accept the ID separately.
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
