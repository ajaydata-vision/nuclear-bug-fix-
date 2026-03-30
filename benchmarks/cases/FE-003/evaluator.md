# Evaluator

## Metadata

- id: FE-003
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react, react-router, useEffect, dependency-array, navigation

## Ground Truth

- root_cause: The useEffect dependency array is empty so it only runs on mount. When the route param changes the component does not remount and the effect never re-fires.
- why_it_happens: An empty dependency array [] tells React to run the effect once on mount. Changing the URL param does not unmount the component so the effect never runs again.
- accepted_fix: Add userId to the dependency array: useEffect(() => { fetchUser(userId).then(setUser) }, [userId])
- rejected_fix_patterns:
  - add key prop to force remount instead of fixing dependency
  - move fetch to parent component as workaround

## Evidence Signals

- strongest_signal: Hard refresh loads correctly but in-app navigation does not
- strongest_alternative_explanation: React Router caching the previous route
- why_alternative_is_wrong: React Router does not cache route data; the component itself is not refetching because the effect is missing the dependency

## Scoring Notes

- full_credit_conditions:
  - identifies missing userId in dependency array
  - proposes adding userId to deps
  - does not suggest key-based remount as the primary fix
- partial_credit_conditions:
  - identifies effect not re-running but proposes key remount workaround
- fail_conditions:
  - blames React Router caching
  - suggests moving to class components
