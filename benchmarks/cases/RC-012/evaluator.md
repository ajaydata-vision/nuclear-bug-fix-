# Evaluator

## Metadata

- id: RC-012
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: batch, race, payment, duplicate-charge, atomic-claim, distributed

## Ground Truth

- root_cause: Multiple workers race on the same subscriptions: all read 'active' before any updates the status to 'charged'.
- why_it_happens: The read-check-write pattern is not atomic. Between reading the status and updating it, other workers can read the same 'active' status and process the same subscription.
- accepted_fix: Use atomic claim with SELECT FOR UPDATE SKIP LOCKED: UPDATE subscriptions SET status='processing' WHERE id = (SELECT id FROM subscriptions WHERE status='active' AND due_date <= now() FOR UPDATE SKIP LOCKED LIMIT 1) RETURNING *. Only the row that is claimed gets processed.
- rejected_fix_patterns:
  - use distributed locks with Redis per subscription ID (correct but more complex than DB-level claim)
  - run only one worker at a time (eliminates parallelism)

## Evidence Signals

- strongest_signal: Duplicate charges correlate with multi-worker execution; all duplicates involve the same subscription being charged multiple times
- strongest_alternative_explanation: Payment provider processing payment twice
- why_alternative_is_wrong: Two separate charge requests are sent to the payment provider; the duplication is in the application before the API call

## Scoring Notes

- full_credit_conditions:
  - identifies TOCTOU race on status check across workers
  - proposes SELECT FOR UPDATE SKIP LOCKED for atomic claim
  - explains why the read-check-write is not atomic
- partial_credit_conditions:
  - identifies the race but proposes distributed locks without explaining why DB-level is simpler
- fail_conditions:
  - adds try/catch around the charge without preventing the duplicate
  - suggests running only one worker
