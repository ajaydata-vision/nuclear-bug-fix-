# Evaluator

## Metadata

- id: IN-007
- domain: integration
- track: distributed-multi-factor
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kafka, at-least-once, idempotency, duplicate, consumer-restart

## Ground Truth

- root_cause: Kafka's at-least-once delivery means messages can be redelivered after a consumer restart if the offset was not committed before the crash. The handler is not idempotent.
- why_it_happens: Kafka guarantees at-least-once delivery by default. If the offset commit fails (e.g., crash between processing and commit), the message is redelivered on restart. Without idempotency, this creates duplicates.
- accepted_fix: Make the handler idempotent: check if an order with the same correlation_id already exists before creating. Use INSERT ... ON CONFLICT DO NOTHING with a unique constraint on correlation_id.
- rejected_fix_patterns:
  - use exactly-once semantics (Kafka transactions) without understanding the complexity
  - retry on duplicate key errors instead of preventing them

## Evidence Signals

- strongest_signal: Duplicates have identical correlation_id; timing correlates with consumer restarts; Kafka at-least-once is the delivery guarantee
- strongest_alternative_explanation: Bug in the producer sending the same message twice
- why_alternative_is_wrong: The message offset is the same for both deliveries; the producer sent it once; the issue is consumer restart causing redelivery

## Scoring Notes

- full_credit_conditions:
  - identifies at-least-once redelivery on restart
  - proposes idempotency check using correlation_id unique constraint
  - explains offset commit gap
- partial_credit_conditions:
  - identifies duplicate processing but proposes catch on duplicate key error
- fail_conditions:
  - enables auto-commit without addressing idempotency
  - blames Kafka for sending duplicates
