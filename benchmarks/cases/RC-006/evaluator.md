# Evaluator

## Metadata

- id: RC-006
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: deadlock, database, transaction, lock-order, postgres, pg

## Ground Truth

- root_cause: Two concurrent transactions acquire locks in opposite order. Transaction A locks account 1 then waits for account 2; Transaction B locks account 2 then waits for account 1.
- why_it_happens: Deadlocks occur when transactions acquire shared resources in different orders. The solution is to enforce a canonical lock acquisition order regardless of transfer direction.
- accepted_fix: Always acquire locks in the same order (e.g., by account ID ascending): const [firstId, secondId] = [accountId1, accountId2].sort(); lock(firstId); lock(secondId).
- rejected_fix_patterns:
  - add retry on deadlock as the only fix (does not prevent future deadlocks)
  - use a single global lock for all transfers (serializes all transfers)

## Evidence Signals

- strongest_signal: PostgreSQL deadlock error explicitly shows two transactions each waiting for the other; lock order is opposite in the two code paths
- strongest_alternative_explanation: Long-running transactions holding locks unnecessarily
- why_alternative_is_wrong: The deadlock is structural (opposite lock order) not temporal (long duration); it occurs regardless of transaction speed

## Scoring Notes

- full_credit_conditions:
  - identifies opposite lock acquisition order as the cause
  - proposes canonical ordering by account ID
  - explains why consistent ordering prevents deadlock
- partial_credit_conditions:
  - adds deadlock retry without fixing the ordering
- fail_conditions:
  - adds a global transaction lock serializing all transfers
  - suggests disabling transactions
