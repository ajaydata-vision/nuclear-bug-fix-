# Evaluator

## Metadata

- id: IN-003
- domain: integration
- track: distributed-multi-factor
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: webhook, idempotency, deduplication, retry, at-least-once

## Ground Truth

- root_cause: The webhook handler does not check for duplicate event IDs before processing, so provider retries on timeout create duplicate operations.
- why_it_happens: Webhook providers use at-least-once delivery: they retry on timeout or failure. Handlers must be idempotent — processing the same event ID twice should produce the same result as processing it once.
- accepted_fix: Store processed event IDs and check before processing: if (await db.webhookEvents.exists({ eventId })) return res.sendStatus(200). Process within a transaction.
- rejected_fix_patterns:
  - increase the webhook timeout limit only
  - deduplicate by checking order existence (insufficient — order may exist from other paths)

## Evidence Signals

- strongest_signal: Same event ID delivered twice; duplicate correlates with near-timeout delivery time
- strongest_alternative_explanation: Bug in order creation causing duplicates
- why_alternative_is_wrong: Duplicates only occur with retried events; the event ID is identical proving it is the same delivery

## Scoring Notes

- full_credit_conditions:
  - identifies missing idempotency check on event ID
  - proposes storing and checking event IDs
  - explains at-least-once delivery semantics
- partial_credit_conditions:
  - identifies duplicate processing but proposes only increasing timeout
- fail_conditions:
  - blames provider for sending duplicates
  - adds client-side deduplication
