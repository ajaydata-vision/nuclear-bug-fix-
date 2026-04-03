# Evaluator

## Metadata

- id: RN-005
- domain: mobile
- track: bohrbug-core
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, reanimated, worklet, ui-thread, gesture-handler, runOnJS

## Ground Truth

- root_cause: `onDismiss()` is called directly inside `useAnimatedGestureHandler`'s `onActive` callback, which runs as a worklet on the UI thread. Regular JavaScript functions cannot be called from the UI thread without an explicit bridge. `threshold` (a plain number primitive) is safe to access from a worklet via closure — primitive values are serialized at worklet definition time.
- why_it_happens: Reanimated 3 runs gesture handler callbacks on the UI thread for performance. The UI thread can read primitive values (numbers, strings) captured at worklet creation time, but cannot synchronously invoke JS-side functions. `onDismiss` is a plain JS callback prop — not a worklet. Calling it directly from `onActive` triggers Reanimated's UI thread guard.
- accepted_fix: Wrap the JS function call with `runOnJS`: `runOnJS(onDismiss)()`. No change to `threshold` is needed — primitive props are safe in worklets.
- rejected_fix_patterns:
  - wrap the entire gesture handler in try/catch
  - convert threshold to a SharedValue (unnecessary — primitive props work in worklets)
  - move the threshold check to onEnd instead of fixing the runOnJS pattern

## Evidence Signals

- strongest_signal: Error message explicitly says "non-worklet function on the UI thread"; crash location is `onActive`; `onDismiss()` is called directly without `runOnJS`; crash only in production where Hermes runs worklets truly on UI thread
- strongest_alternative_explanation: A version incompatibility between react-native-gesture-handler and react-native-reanimated
- why_alternative_is_wrong: The error message "Tried to synchronously call a non-worklet function" is emitted by Reanimated's own runtime guard, not by gesture-handler. Version incompatibilities between these libraries produce different error messages (typically about missing native modules or gesture state).

## Scoring Notes

- full_credit_conditions:
  - identifies direct JS function call (onDismiss) from worklet as the crash cause
  - prescribes runOnJS(onDismiss)() as the fix
  - correctly notes threshold does NOT need changing (it is a safe primitive)
- partial_credit_conditions:
  - prescribes runOnJS correctly but also unnecessarily converts threshold to SharedValue
  - identifies the worklet boundary issue but does not name runOnJS specifically
- fail_conditions:
  - blames gesture-handler version incompatibility
  - suggests try/catch as the fix
  - identifies threshold as the crash cause rather than onDismiss
