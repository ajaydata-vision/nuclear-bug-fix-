# Evaluator

## Metadata

- id: RC-008
- domain: general
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: flaky-test, shared-state, jest, ci, test-order

## Ground Truth

- root_cause: Another test contaminates shared global state, so the failing test depends on suite order.
- why_it_happens: The test assumes a clean global flag state that is not fully reset between tests.
- accepted_fix: Isolate or reset shared state before each test, or avoid mutable globals entirely.
- rejected_fix_patterns:
  - increase test timeout
  - rerun flaky tests until pass
  - blame CI hardware

## Evidence Signals

- strongest_signal: The test passes alone but fails in suite order alongside a state-mutating test
- strongest_alternative_explanation: The code under test is truly nondeterministic
- why_alternative_is_wrong: Isolation makes the failure disappear and another test directly mutates the same global

## Scoring Notes

- full_credit_conditions:
  - identifies order-dependent shared-state contamination
  - proposes `beforeEach` reset or removal of mutable global coupling
  - verification includes random-order rerun
- partial_credit_conditions:
  - identifies a flaky test but gives only general advice
- fail_conditions:
  - blames async timing without evidence
  - suggests suppressing the test
