# Evaluator

## Metadata

- id: FE-002
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react, closure, stale-state, hooks, counter

## Ground Truth

- root_cause: The closure captures a stale value of count at the time of the click, so all queued callbacks increment from the same baseline.
- why_it_happens: Each setTimeout callback closes over the count at the time the handler ran. With rapid clicks all closures see count=0 and all set count to 1.
- accepted_fix: Use the functional form of setState: setCount(prev => prev + 1)
- rejected_fix_patterns:
  - add debounce to the click handler
  - increase setTimeout delay
  - use useRef to store count

## Evidence Signals

- strongest_signal: Multiple clicks produce final count of 1 regardless of click speed
- strongest_alternative_explanation: Race condition between setState calls
- why_alternative_is_wrong: The issue is deterministic and reproducible with any delay; it is a closure capture issue not a scheduling race

## Scoring Notes

- full_credit_conditions:
  - identifies stale closure over count
  - proposes functional setState update
  - does not suggest debounce as root fix
- partial_credit_conditions:
  - spots setState issue but frames it as async/timing problem
- fail_conditions:
  - adds debounce as the fix
  - suggests useRef as the solution
