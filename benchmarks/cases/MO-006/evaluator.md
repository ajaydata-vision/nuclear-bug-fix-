# Evaluator

## Metadata

- id: MO-006
- domain: frontend
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, deep-link, navigation, cold-start, initial-route

## Ground Truth

- root_cause: The navigation call runs before the navigator has finished initializing, so the navigation is dropped or overridden by the initial route.
- why_it_happens: On cold start the navigator needs time to initialize. Calling navigate() before the navigator is ready results in a no-op or the initial route overrides the navigation.
- accepted_fix: Use React Navigation's linking configuration to handle initial URL before the navigator renders, or check navigator.isReady() before navigating and defer if not ready.
- rejected_fix_patterns:
  - add a setTimeout delay before navigating
  - store the URL and navigate on next render without checking ready state

## Evidence Signals

- strongest_signal: Deep link works when app is running (navigator already ready) but fails on cold start (navigator not yet ready)
- strongest_alternative_explanation: Deep link URL parsing error
- why_alternative_is_wrong: The URL is received correctly (getLinking returns it); the issue is timing of navigation not URL parsing

## Scoring Notes

- full_credit_conditions:
  - identifies navigator not ready on cold start
  - proposes React Navigation linking config or isReady() check
  - explains initial route override
- partial_credit_conditions:
  - identifies timing issue but proposes setTimeout workaround
- fail_conditions:
  - blames OS deep link handling
  - adds URL validation without fixing timing
