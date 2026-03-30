# Evaluator

## Metadata

- id: MO-002
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: react-native, ios, safe-area, notch, layout

## Ground Truth

- root_cause: The layout does not account for iOS safe area insets, so content extends into the home indicator area on modern iPhones.
- why_it_happens: Modern iPhones with Face ID have home indicator insets at the bottom. React Native's SafeAreaView or useSafeAreaInsets hook must be used to pad content away from these areas.
- accepted_fix: Wrap with SafeAreaView from react-native-safe-area-context or apply useSafeAreaInsets().bottom as padding to the bottom navigation.
- rejected_fix_patterns:
  - hardcode a fixed bottom padding of 34px
  - hide the bottom tab bar on newer iOS

## Evidence Signals

- strongest_signal: Only affects iPhones with Face ID; content is cut off exactly at the home indicator boundary
- strongest_alternative_explanation: React Navigation misconfiguration
- why_alternative_is_wrong: The tab bar is visible on the screen; it is the content below it that is obscured by the OS UI element

## Scoring Notes

- full_credit_conditions:
  - identifies missing safe area inset handling
  - proposes SafeAreaView or useSafeAreaInsets
  - explains Dynamic Island/home indicator difference
- partial_credit_conditions:
  - identifies inset issue but proposes hardcoded value
- fail_conditions:
  - blames React Native bug
  - applies fix only to specific iPhone models
