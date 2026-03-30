# Evaluator

## Metadata

- id: RC-002
- domain: general
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: toctou, inventory, race, postgres, checkout

## Ground Truth

- root_cause: The inventory flow separates the availability check from the decrement, creating a TOCTOU race.
- why_it_happens: Two transactions both observe the same pre-update stock before either mutation commits.
- accepted_fix: Collapse check and decrement into one atomic SQL statement or lock the row during the operation.
- rejected_fix_patterns:
  - add retry loops without atomic guard
  - trust application-level pre-checks
  - remove oversell alerts only

## Evidence Signals

- strongest_signal: Both requests pass the same check before the write
- strongest_alternative_explanation: Stock count was already wrong before checkout
- why_alternative_is_wrong: Reproduction starts from a known stock count of 1 and only fails under concurrency

## Scoring Notes

- full_credit_conditions:
  - names TOCTOU explicitly
  - proposes atomic `UPDATE ... WHERE count > 0` or row lock
  - verification includes concurrent last-item purchase
- partial_credit_conditions:
  - identifies race but proposes broad mutex without considering DB atomicity
- fail_conditions:
  - blames UI double submit only
  - keeps separate check and update as the core logic
