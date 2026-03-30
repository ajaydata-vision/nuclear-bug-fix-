# Evaluator

## Metadata

- id: RC-013
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: distributed-lock, redis, ttl, crash, deadlock, setnx

## Ground Truth

- root_cause: The distributed lock is set without an expiry (TTL). If the process crashes before releasing it, the lock persists forever.
- why_it_happens: Redis SETNX without a TTL creates a permanent key. A crashed process cannot release a lock it holds. Without TTL the lock becomes a permanent block.
- accepted_fix: Use SET key value NX EX timeout (atomic set-if-not-exists with TTL): await redis.set('lock:report', '1', 'NX', 'EX', 30). The TTL ensures automatic release on crash. Make the timeout longer than the maximum expected operation duration.
- rejected_fix_patterns:
  - manually delete the lock key in Redis as the long-term fix
  - disable distributed locking

## Evidence Signals

- strongest_signal: Lock key in Redis with no TTL; timing matches process crash; operation permanently blocked
- strongest_alternative_explanation: Lock released by another process before report completes
- why_alternative_is_wrong: The lock is present and permanent (no TTL); the operation is blocked not completing incorrectly

## Scoring Notes

- full_credit_conditions:
  - identifies missing TTL on lock acquisition
  - proposes SET NX EX with appropriate timeout
  - explains why atomic set-with-TTL prevents the permanent lock scenario
- partial_credit_conditions:
  - deletes the current stuck lock and adds TTL but uses two separate commands (not atomic)
- fail_conditions:
  - suggests increasing Redis memory to prevent eviction
  - manually deletes the lock as the complete solution
