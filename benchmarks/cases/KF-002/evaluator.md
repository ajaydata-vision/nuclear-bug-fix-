# Evaluator

## Metadata

- id: KF-002
- domain: java-enterprise
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kafka, consumer, rebalance, max-poll-interval-ms, duplicate-processing, spring-kafka

## Ground Truth

- root_cause: The `@KafkaListener` method takes 47 seconds to process one message. The application has `max.poll.interval.ms: 30000` (30 seconds) explicitly configured. A single message processing for 47 seconds exceeds this 30-second threshold, causing the Kafka coordinator to declare the consumer dead and trigger a rebalance. The partition is reassigned and the unacknowledged message is replayed, creating duplicate payment records.
- why_it_happens: Kafka requires that a consumer call `poll()` within `max.poll.interval.ms`. When `ack-mode: batch`, Spring Kafka processes all records in a batch then commits. If any poll cycle takes longer than `max.poll.interval.ms`, the coordinator evicts the consumer before the commit, the partition is reassigned to another consumer (or this one after rejoin), and processing starts from the last committed offset — replaying unacknowledged messages.
- accepted_fix: Reduce `max-poll-records` to 1 (process one message at a time for slow operations) OR increase `max.poll.interval.ms` to safely exceed worst-case batch processing time OR switch `ack-mode: record` to commit after each message. For idempotency: add a processed-payment check before saving to prevent duplicate database records regardless of rebalance.
- rejected_fix_patterns:
  - add a try/catch around the listener method
  - increase consumer thread count
  - disable rebalancing (not possible in standard Kafka)

## Evidence Signals

- strongest_signal: Logs show rebalance triggering after a 47-second processing window; same message key appears twice after Revoked/Assigned cycle; `max.poll.interval.ms: 30000` in application.yml — 47s exceeds 30s threshold directly
- strongest_alternative_explanation: A network interruption between consumer and Kafka broker causes session timeout and rebalance
- why_alternative_is_wrong: Network interruptions cause `session.timeout.ms`-based rebalances, which occur DURING processing when heartbeats stop. The logs show the rebalance triggering AFTER a 47-second processing window completes — timing correlates with processing duration, not random network events. The explicit `max.poll.interval.ms: 30000` and 47-second processing time make the cause deterministic for slow messages.

## Scoring Notes

- full_credit_conditions:
  - identifies max.poll.interval.ms exceeded by long processing time as root cause
  - connects max-poll-records=50 to the batch processing time calculation
  - prescribes reducing max-poll-records OR increasing max.poll.interval.ms OR record-level ack
  - mentions idempotency check to handle duplicates already in database
- partial_credit_conditions:
  - correctly identifies rebalance from processing timeout but only prescribes one fix without mentioning idempotency for existing duplicates
  - identifies session.timeout.ms as the threshold (incorrect — it is max.poll.interval.ms for processing time, but shows understanding of the mechanism)
- fail_conditions:
  - blames network connectivity
  - suggests consumer thread count as the fix
  - recommends disabling auto-commit without explaining the rebalance root cause
