# Evaluator

## Metadata

- id: RC-001
- domain: general
- track: intermittent-race
- difficulty: easy
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: race, counter, atomic, goroutine, shared-state

## Ground Truth

- root_cause: Unsynchronized read-modify-write access to shared state creates a classic data race.
- why_it_happens: Multiple goroutines read the same old value and overwrite each other's increment.
- accepted_fix: Use `sync/atomic` or a mutex around the increment.
- rejected_fix_patterns:
  - add sleep
  - blame integer overflow
  - move the read to another function without synchronization

## Evidence Signals

- strongest_signal: Lost increments appear only under parallel access and the code performs non-atomic mutation
- strongest_alternative_explanation: The final read happens too early
- why_alternative_is_wrong: Even after all goroutines complete, the final value is still lower than expected

## Scoring Notes

- full_credit_conditions:
  - identifies data race
  - proposes atomic or mutex fix
  - verification includes concurrent rerun or `go test -race`
- partial_credit_conditions:
  - spots concurrency issue but proposes heavy redesign only
- fail_conditions:
  - blames arithmetic or test timing only
  - adds sleeps as the fix
