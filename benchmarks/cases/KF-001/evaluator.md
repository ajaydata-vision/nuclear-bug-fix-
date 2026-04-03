# Evaluator

## Metadata

- id: KF-001
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kafka, consumer, auto-offset-reset, group-id, spring-kafka, lag

## Ground Truth

- root_cause: The consumer group `order-processor-v1` is brand new and has no committed offsets. Kafka's default `auto.offset.reset=latest` causes the consumer to start reading from the END of each partition — all messages produced before the consumer first joined are permanently skipped.
- why_it_happens: When a consumer group has no committed offset for a partition, Kafka uses `auto.offset.reset` to determine the starting position. The default is `latest`, which sets the initial offset to the current log-end-offset. CURRENT-OFFSET = LOG-END-OFFSET = LAG of 0 is the smoking gun: the consumer successfully joined and committed its starting position at the end of the log, meaning every previously produced message is already "behind" the consumer's starting point.
- accepted_fix: Set `auto.offset.reset=earliest` in `application.yml` AND delete the consumer group's committed offsets (so Kafka re-applies the reset policy): `kafka-consumer-groups.sh --bootstrap-server kafka:9092 --group order-processor-v1 --reset-offsets --to-earliest --topic orders --execute`. For new consumer groups that must read historical data, always configure `earliest` before the group's first connection.
- rejected_fix_patterns:
  - restart the consumer without changing auto.offset.reset (group already has committed offsets at log-end, reset policy only applies when no offset exists)
  - increase the consumer's poll timeout
  - check the deserializer configuration (messages are not even reaching the deserializer)

## Evidence Signals

- strongest_signal: CURRENT-OFFSET equals LOG-END-OFFSET with LAG=0 for all partitions on a brand-new consumer group — the consumer joined and positioned itself at the end of the log, skipping all prior messages
- strongest_alternative_explanation: The `@KafkaListener` method is not being invoked due to a Spring bean misconfiguration or the container not starting
- why_alternative_is_wrong: The kafka-consumer-groups.sh output shows the consumer IS connected (CONSUMER-ID is populated) and has committed offsets matching LOG-END-OFFSET. A misconfigured listener would show no CONSUMER-ID or would show the group as not active. LAG=0 with an active consumer-id proves the consumer is running and positioned correctly — just at the wrong position.

## Scoring Notes

- full_credit_conditions:
  - identifies auto.offset.reset=latest as root cause
  - explains that LAG=0 on a new group means consumer started at end of log
  - prescribes setting earliest AND resetting committed offsets
- partial_credit_conditions:
  - correctly identifies auto.offset.reset but only says "change to earliest" without noting that existing committed offsets must also be reset
  - identifies the LAG=0 smoking gun but frames fix as "restart consumer"
- fail_conditions:
  - diagnoses deserializer mismatch
  - blames group.id configuration without explaining offset position
  - suggests checking network connectivity to Kafka
