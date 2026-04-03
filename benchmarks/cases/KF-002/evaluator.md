# Evaluator

## Metadata

- id: KF-002
- domain: java-enterprise
- track: intermittent-race
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kafka, consumer, rebalance, max-poll-interval-ms, duplicate-processing, spring-kafka

## Ground Truth

- root_cause: The `@KafkaListener` method takes 47 seconds to process one message. Kafka's `max.poll.interval.ms` defaults to 300,000ms (5 minutes) BUT `max-poll-records: 50` means the consumer may poll a batch of 50 messages and must process all 50 within that window. With a 47-second per-message processing time and 50 records per poll, the total batch time can exceed `max.poll.interval.ms`, causing the coordinator to declare the consumer dead and trigger a rebalance. The rebalance resets the partition to the last committed offset, replaying already-processed messages.
- why_it_happens: Kafka requires that a consumer call `poll()` within `max.poll.interval.ms`. When `ack-mode: batch`, Spring Kafka commits offsets after the entire batch is processed. If the batch takes longer than `max.poll.interval.ms`, the coordinator kicks out the consumer before the commit, the partition is reassigned, and the next consumer (or this one, after rejoin) re-processes from the last committed point — causing duplicates.
- accepted_fix: Reduce `max-poll-records` to 1 (process one message at a time for slow operations) OR increase `max.poll.interval.ms` to safely exceed worst-case batch processing time OR switch `ack-mode: record` to commit after each message. For idempotency: add a processed-payment check before saving to prevent duplicate database records regardless of rebalance.
- rejected_fix_patterns:
  - add a try/catch around the listener method
  - increase consumer thread count
  - disable rebalancing (not possible in standard Kafka)

## Evidence Signals

- strongest_signal: Logs show rebalance triggering immediately after a 47-second processing window; same message key appears twice in sequence after Revoked/Assigned cycle; processing time (47s) plus batch size (50) can exceed max.poll.interval.ms
- strongest_alternative_explanation: A network interruption between consumer and Kafka broker causes session timeout and rebalance
- why_alternative_is_wrong: A network interruption would cause a session.timeout.ms-based rebalance (default 45s) which would not correlate with message processing completion. The logs show rebalance happening AFTER a 47-second processing window completes — network issues cause rebalances during processing, not after. The pattern is deterministic with slow messages.

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
