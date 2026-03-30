# Evaluator

## Metadata

- id: MO-001
- domain: mobile
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, ios, native-module, pods, bridge

## Ground Truth

- root_cause: The native iOS dependency is not linked or installed correctly, so the JS layer references a module the native runtime never registered.
- why_it_happens: The JS import exists, but the iOS native side was not rebuilt with the required pod or native integration.
- accepted_fix: Install or relink the iOS native dependency, run `pod install`, and rebuild the app.
- rejected_fix_patterns:
  - blame React state or navigation
  - add null guards around the module only
  - treat Android success as proof the package is linked everywhere

## Evidence Signals

- strongest_signal: The failure is platform-specific and names a missing native module directly
- strongest_alternative_explanation: Camera permission is missing
- why_alternative_is_wrong: Missing permission would not make the native module object itself null at bridge load time

## Scoring Notes

- full_credit_conditions:
  - identifies native linking / pods / rebuild problem
  - proposes iOS native install and rebuild
  - verification includes reopening the screen after rebuild
- partial_credit_conditions:
  - identifies native integration issue but misses pods specifically
- fail_conditions:
  - blames JS rendering
  - focuses only on permissions
