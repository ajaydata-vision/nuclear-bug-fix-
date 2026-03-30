# Evaluator

## Metadata

- id: IN-005
- domain: integration
- track: distributed-multi-factor
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: rabbitmq, ack, message-loss, at-least-once, premature-ack

## Ground Truth

- root_cause: Messages are acknowledged before processing completes. If processing fails, the message has already been removed from the queue and cannot be retried.
- why_it_happens: RabbitMQ (and AMQP) remove messages from the queue upon acknowledgement. Acking before processing means failures result in permanent message loss rather than redelivery.
- accepted_fix: Move the ack after successful processing: await processOrder(msg); channel.ack(msg). Use channel.nack(msg, false, true) on failure to requeue.
- rejected_fix_patterns:
  - add try/catch around processOrder without fixing the ack position
  - use auto-ack mode

## Evidence Signals

- strongest_signal: Messages consumed and acknowledged but some orders missing; no dead-letter entries; error in processOrder causes silent drop
- strongest_alternative_explanation: Bug in processOrder corrupting data
- why_alternative_is_wrong: processOrder throws an exception; the message is already acked so the exception has no retry path

## Scoring Notes

- full_credit_conditions:
  - identifies premature ack before processing
  - proposes ack after success and nack on failure
  - explains RabbitMQ ack semantics
- partial_credit_conditions:
  - identifies the ack position but does not address nack for failure cases
- fail_conditions:
  - adds error logging without fixing ack position
  - switches to auto-ack mode
