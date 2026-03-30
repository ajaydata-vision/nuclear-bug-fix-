# Evaluator

## Metadata

- id: FE-018
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: react, useEffect, infinite-loop, dependency-array, object-reference

## Ground Truth

- root_cause: options is an object literal defined inside the component body. Every render creates a new object reference, so React sees the dependency as changed every time.
- why_it_happens: React compares dependency array values by reference (===). A new object literal has a new reference on every render even if the values are identical, causing useEffect to run every render, which triggers another render.
- accepted_fix: Move the options object outside the component, use useMemo to memoize it, or use primitive values as dependencies instead of the object.
- rejected_fix_patterns:
  - wrap the entire component in React.memo
  - add JSON.stringify(options) as the dependency

## Evidence Signals

- strongest_signal: Thousands of renders per second immediately on mount; dependency is an object literal
- strongest_alternative_explanation: Infinite setState loop inside the effect
- why_alternative_is_wrong: The effect calls fetchData which does not call setState; the loop is caused by dependency comparison not state mutation

## Scoring Notes

- full_credit_conditions:
  - identifies object reference changing on every render
  - proposes useMemo or moving object outside component
  - explains reference equality
- partial_credit_conditions:
  - identifies useEffect loop but suggests JSON.stringify workaround
- fail_conditions:
  - adds isLoading guard inside effect without fixing dependency
  - suggests wrapping in React.memo
