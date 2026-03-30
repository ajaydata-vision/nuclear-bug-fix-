# Evaluator

## Metadata

- id: IN-006
- domain: integration
- track: distributed-multi-factor
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kafka, consumer-lag, performance, db-query, n-plus-one, bottleneck

## Ground Truth

- root_cause: Each message triggers a separate synchronous database query (200ms), limiting throughput to ~5 messages/second per consumer. The queue produces 500/s.
- why_it_happens: Synchronous per-message DB queries make the consumer throughput bounded by query latency. At 200ms per query, maximum is 5 msg/s; at 500 msg/s production rate, lag grows at 495 msg/s.
- accepted_fix: Batch messages and use IN clause: SELECT * FROM products WHERE id = ANY($1::int[]). Or cache product lookups in memory/Redis to avoid repeated DB hits.
- rejected_fix_patterns:
  - add more consumer instances as the only fix
  - increase Kafka partition count only

## Evidence Signals

- strongest_signal: Consumer processes 100ms/msg from DB query; 500 msg/s producer rate; lag math confirms the throughput mismatch
- strongest_alternative_explanation: Kafka partition count too low
- why_alternative_is_wrong: Adding partitions helps with parallelism but does not fix per-message DB cost; with batching a single consumer can keep up

## Scoring Notes

- full_credit_conditions:
  - identifies per-message DB query as the bottleneck
  - proposes batching with IN clause or caching
  - calculates the throughput mismatch
- partial_credit_conditions:
  - identifies consumer lag but proposes only adding more consumers without addressing query cost
- fail_conditions:
  - blames Kafka cluster performance
  - suggests increasing message batch size without changing the query
