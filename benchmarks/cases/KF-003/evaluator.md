# Evaluator

## Metadata

- id: KF-003
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kafka, consumer, poison-pill, deserializer, ErrorHandlingDeserializer, dead-letter-queue, spring-kafka

## Ground Truth

- root_cause: A malformed JSON message at partition 1 offset 94821 causes `JsonDeserializer` to throw on every poll attempt. Without `ErrorHandlingDeserializer` configured, Spring Kafka retries the same offset indefinitely — "Seeking to current position" confirms it is re-attempting the same offset each time. The partition is permanently blocked until the offset is manually skipped or the deserializer is made fault-tolerant.
- why_it_happens: Kafka's at-least-once delivery guarantees that the consumer retries a failed offset until it succeeds or the offset is explicitly advanced. `JsonDeserializer` throws before the `@KafkaListener` method is invoked, so no application-level error handler can intercept it. The only way out of this loop without code change is to skip the offset manually or add `ErrorHandlingDeserializer` which catches deserialization failures and delivers them as `DeserializationException`-annotated records that the application can handle and route to a DLQ.
- accepted_fix: Configure `ErrorHandlingDeserializer` as the value deserializer, delegating to `JsonDeserializer`. In the `@KafkaListener`, check for the `DESERIALIZER_EXCEPTION_HEADER` header and route poison pills to a dead-letter topic. Immediate recovery: manually skip offset 94821 using `kafka-consumer-groups.sh --reset-offsets --to-offset 94822 --topic notifications:1 --execute`.
- rejected_fix_patterns:
  - restart the consumer (same offset will be retried after restart)
  - add try/catch inside the @KafkaListener method (deserialization failure occurs before the method is called)
  - increase consumer memory or thread count

## Evidence Signals

- strongest_signal: "Seeking to current position for [notifications-1@offset 94821]" repeating identically — same partition, same offset, every retry; JsonParseException at the exact same offset; partitions 0 and 2 processing normally
- strongest_alternative_explanation: A consumer thread is deadlocked or the notification service is throwing an exception causing the consumer to retry
- why_alternative_is_wrong: A deadlock would block ALL partitions since Spring Kafka's default listener container uses shared threads. Only partition 1 is blocked, and the error is a deserialization exception — which occurs before the `notificationService.send()` call. The log shows JsonParseException in the converter layer, not in the application method.

## Scoring Notes

- full_credit_conditions:
  - identifies malformed message (poison pill) causing infinite deserialization retry as root cause
  - explains why try/catch in the listener method cannot help (failure is before method invocation)
  - prescribes ErrorHandlingDeserializer configuration
  - includes immediate recovery: manually advancing the offset past 94821
- partial_credit_conditions:
  - correctly identifies poison pill and ErrorHandlingDeserializer but omits the immediate offset-skip recovery step
  - prescribes DLQ routing but does not explain how to unblock the current stuck offset
- fail_conditions:
  - recommends restarting the consumer as the fix
  - adds try/catch inside @KafkaListener as the primary fix
  - blames the producer without prescribing a consumer-side fix
