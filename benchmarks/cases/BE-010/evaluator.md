# Evaluator

## Metadata

- id: BE-010
- domain: backend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: queue, background-job, error-handling, dead-letter, bull, rabbitmq

## Ground Truth

- root_cause: Errors are caught and logged but not re-thrown, so BullMQ considers the job successful and removes it from the queue instead of marking it failed.
- why_it_happens: BullMQ (and most queue libraries) determine job success or failure based on whether the job processor throws. Swallowing the error makes the framework believe the job completed successfully.
- accepted_fix: Re-throw the error after logging: throw err inside the catch block, or return Promise.reject(err). This allows BullMQ to mark the job as failed and retry or move to dead-letter queue.
- rejected_fix_patterns:
  - add the job to a separate error log table manually
  - disable job retry to prevent duplicate processing

## Evidence Signals

- strongest_signal: Jobs consumed with no output and no failures; error swallowed in catch block
- strongest_alternative_explanation: Email provider outage
- why_alternative_is_wrong: The error is caught and ignored so the job succeeds from the queue's perspective regardless of the email outcome

## Scoring Notes

- full_credit_conditions:
  - identifies swallowed error preventing job failure
  - proposes re-throwing the error
  - explains how BullMQ determines job success
- partial_credit_conditions:
  - identifies the catch block but proposes only better logging
- fail_conditions:
  - blames email provider
  - suggests checking Redis health
