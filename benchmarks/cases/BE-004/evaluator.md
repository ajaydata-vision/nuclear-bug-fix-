# Evaluator

## Metadata

- id: BE-004
- domain: backend
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: timeout, async, response-sent-after-timeout, duplicate-operation, retry

## Ground Truth

- root_cause: The operation exceeds the load balancer timeout so the client gets a 504, but the server continues and completes the work, causing duplicates on retry.
- why_it_happens: The load balancer disconnects after its timeout but the server process keeps running. The client has no way to know if the operation succeeded, so retrying creates duplicates.
- accepted_fix: Use async job pattern: return a job ID immediately (202 Accepted), process in background, allow client to poll for status. Add idempotency key to prevent duplicate creation on retry.
- rejected_fix_patterns:
  - increase load balancer timeout to 60s
  - add retry logic on client without idempotency

## Evidence Signals

- strongest_signal: DB has the record but client got 504; operation log shows completion after timeout
- strongest_alternative_explanation: Database transaction rolled back on timeout
- why_alternative_is_wrong: The record exists in the database, proving the transaction committed successfully

## Scoring Notes

- full_credit_conditions:
  - identifies timeout/completion race
  - proposes async job + idempotency
  - explains the duplicate creation problem
- partial_credit_conditions:
  - identifies the timing issue but proposes only increasing timeout
- fail_conditions:
  - proposes client-side retry without idempotency
  - suggests cancelling the DB operation on timeout
