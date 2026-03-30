# Evaluator

## Metadata

- id: MO-007
- domain: frontend
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: false
- tags: react-native, ios, app-store, permissions, info-plist, rejection

## Ground Truth

- root_cause: The Info.plist is missing the NSCameraUsageDescription key that Apple requires for any app that requests camera access, regardless of whether permission is runtime-only.
- why_it_happens: Apple's App Review automatically checks for any API usage that requires a permission string in Info.plist. Even if permissions are requested correctly at runtime, the absence of the usage description string causes automatic rejection.
- accepted_fix: Add NSCameraUsageDescription to Info.plist with a clear user-facing explanation of why the camera is needed.
- rejected_fix_patterns:
  - remove camera functionality
  - add the key with an empty string

## Evidence Signals

- strongest_signal: App Store rejection email names the exact missing key
- strongest_alternative_explanation: Camera permission code broken in production build
- why_alternative_is_wrong: App Store Review catches this before users can even run the app; the rejection is automated based on Info.plist analysis

## Scoring Notes

- full_credit_conditions:
  - identifies missing NSCameraUsageDescription key
  - proposes adding key with meaningful description
  - notes Apple requires this for all camera API usage
- partial_credit_conditions:
  - adds the key but with empty or insufficient description
- fail_conditions:
  - removes camera functionality to avoid the check
  - suggests bypassing App Store review
