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
- tags: dlq, dead-letter-queue, rabbitmq, queue-full, reject-publish, overflow-policy, backpressure

## Ground Truth

- root_cause: The Dead Letter Queue is full because it has no consumer, and its overflow policy is set to reject-publish. Once invalid messages fill the DLQ to capacity, new dead-letter attempts are rejected and backpressure cascades to the main flow.
- why_it_happens: A DLQ without a consumer is a message sink that fills up. With x-overflow set to reject-publish, RabbitMQ refuses additional dead-lettered messages once x-max-length is reached instead of dropping old ones, so nacked invalid messages can no longer be routed.
- accepted_fix: Immediately consume and triage the DLQ backlog. Operationally run a DLQ consumer that alerts on failures and either repairs+requeues or logs+discards with monitoring. Keep alerting on DLQ depth so reject-publish never becomes a surprise bottleneck.
- rejected_fix_patterns:
  - increase x-max-length on the DLQ as the permanent fix
  - drop all messages in the DLQ without investigating

## Evidence Signals

- strongest_signal: DLQ is exactly at x-max-length with x-overflow: reject-publish and no consumer; backpressure started when the DLQ hit capacity
- strongest_alternative_explanation: RabbitMQ broker running out of disk space
- why_alternative_is_wrong: Broker disk is fine; the specific rejection message cites DLQ overflow policy and capacity, not disk; only messages that dead-letter are affected

## Scoring Notes

- full_credit_conditions:
  - identifies reject-publish overflow plus no DLQ consumer as the combined root cause
  - proposes draining the backlog and running a DLQ consumer with triage logic
  - recommends DLQ depth alerting to prevent recurrence
- partial_credit_conditions:
  - identifies the DLQ as the issue but proposes only increasing its size limit
- fail_conditions:
  - adds more main queue consumers
  - purges the DLQ without investigating why messages are invalid
