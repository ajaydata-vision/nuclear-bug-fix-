# Evaluator

## Metadata

- id: FE-017
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: memory-leak, event-listener, cleanup, useEffect, react

## Ground Truth

- root_cause: Event listeners added to window in useEffect are never removed on component unmount, so each mount adds another listener that persists.
- why_it_happens: useEffect cleanup functions remove side effects when the component unmounts. Without a cleanup returning removeEventListener, every mount adds a permanent global listener.
- accepted_fix: Return a cleanup function from useEffect: return () => window.removeEventListener('resize', handleResize)
- rejected_fix_patterns:
  - debounce the resize handler as the primary fix
  - use ref instead of state for resize

## Evidence Signals

- strongest_signal: Event listener count in DevTools grows proportionally to navigation count
- strongest_alternative_explanation: Memory leak in state management
- why_alternative_is_wrong: DevTools shows listener count growing specifically, not heap growth; the cause is deterministically the missing cleanup

## Scoring Notes

- full_credit_conditions:
  - identifies missing removeEventListener cleanup
  - proposes returning cleanup from useEffect
  - explains cumulative listener buildup
- partial_credit_conditions:
  - identifies memory leak but attributes to wrong cause
- fail_conditions:
  - debounces the handler without adding cleanup
  - suggests using React.memo as fix
