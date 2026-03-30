# Evaluator

## Metadata

- id: IN-015
- domain: integration
- track: distributed-multi-factor
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: dlq, dead-letter-queue, rabbitmq, queue-full, message-rejection, backpressure

## Ground Truth

- root_cause: The Dead Letter Queue is full because it has no consumer. Invalid messages fill it to capacity and new failures cannot be routed to it, causing cascading rejection of valid processing.
- why_it_happens: A DLQ without a consumer is a message sink that fills up. When full, RabbitMQ cannot move nacked messages there, blocking the main queue's ability to process invalid messages — and eventually valid ones.
- accepted_fix: Immediately: consume and triage the DLQ backlog. Operationally: run a DLQ consumer that alerts on failures and either repairs+requeues or logs+discards with monitoring. Set up DLQ depth alerting.
- rejected_fix_patterns:
  - increase x-max-length on the DLQ as the permanent fix
  - drop all messages in the DLQ without investigating

## Evidence Signals

- strongest_signal: DLQ at exactly x-max-length limit with no consumer; 3 days of accumulation; backpressure started when DLQ filled
- strongest_alternative_explanation: RabbitMQ broker running out of disk space
- why_alternative_is_wrong: Broker disk is fine; the specific rejection message cites DLQ capacity not disk; only messages with validation failures are affected

## Scoring Notes

- full_credit_conditions:
  - identifies DLQ full with no consumer as root cause
  - proposes DLQ consumer with triage logic
  - recommends DLQ depth alerting to prevent recurrence
- partial_credit_conditions:
  - identifies DLQ as the issue but proposes only increasing its size limit
- fail_conditions:
  - adds more main queue consumers
  - purges the DLQ without investigating why messages are invalid
