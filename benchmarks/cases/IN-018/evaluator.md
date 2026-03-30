# Evaluator

## Metadata

- id: IN-018
- domain: integration
- track: distributed-multi-factor
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: connection-pool, postgres, timeout, pool-exhaustion, node-postgres

## Ground Truth

- root_cause: Slow queries hold connections for the entire query duration. With a pool of 10 and more than 10 concurrent slow queries, all connections are occupied and new requests queue indefinitely.
- why_it_happens: Connection pool size limits the maximum concurrent DB operations. Slow queries multiply the connection hold time. pool_size / query_duration = maximum request rate (10 / 8s = 1.25 req/s).
- accepted_fix: Optimise the slow query with indexes. Increase pool size cautiously (monitor DB max_connections). Add a pool connection timeout. Consider query result caching for expensive read-only queries.
- rejected_fix_patterns:
  - increase pool size to 1000 without fixing slow queries
  - add connection retry without addressing the root exhaustion

## Evidence Signals

- strongest_signal: Pool queue length grows under load; connection hold time matches query duration; math shows pool exhaustion at observed concurrency
- strongest_alternative_explanation: PostgreSQL max_connections reached
- why_alternative_is_wrong: pg pool is the limiting factor here; PostgreSQL max_connections is higher; the pool itself is the bottleneck

## Scoring Notes

- full_credit_conditions:
  - identifies slow query holding connections too long
  - proposes query optimization and appropriate pool sizing
  - calculates the math showing why exhaustion occurs
- partial_credit_conditions:
  - identifies pool exhaustion but only suggests increasing pool size
- fail_conditions:
  - adds connection retry without fixing the slow query
  - blames PostgreSQL performance
