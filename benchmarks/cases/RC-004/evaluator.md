# Evaluator

## Metadata

- id: RC-004
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: cache, stampede, thundering-herd, redis, database, expiry

## Ground Truth

- root_cause: When the cache key expires, all concurrent requests get a cache miss simultaneously and all query the database at once — a cache stampede.
- why_it_happens: Without a lock or probabilistic expiry, every requester that finds an expired key immediately queries the database. With high traffic, this is thousands of simultaneous DB queries for the same data.
- accepted_fix: Use a distributed lock (Redis SETNX) to allow only one request to refresh the cache while others wait. Or use probabilistic early expiry to refresh before the key expires.
- rejected_fix_patterns:
  - increase TTL to reduce expiry frequency
  - add more database replicas as the only fix

## Evidence Signals

- strongest_signal: Database spike correlates exactly with cache TTL expiry interval; hundreds of identical queries for same key
- strongest_alternative_explanation: Scheduled batch job running at the same time
- why_alternative_is_wrong: The spike pattern matches TTL expiry not a fixed clock schedule; timing drifts as the cache is refreshed at different times

## Scoring Notes

- full_credit_conditions:
  - identifies cache stampede on expiry
  - proposes distributed lock or probabilistic early expiry
  - explains thundering herd problem
- partial_credit_conditions:
  - identifies cache expiry as the trigger but proposes only TTL extension
- fail_conditions:
  - adds more DB read replicas without fixing the stampede
  - disables caching
