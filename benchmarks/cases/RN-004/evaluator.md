# Evaluator

## Metadata

- id: RN-004
- domain: mobile
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, ios, permissions, info-plist, camera, NSCameraUsageDescription

## Ground Truth

- root_cause: The `NSCameraUsageDescription` key is absent from `Info.plist`. iOS requires this key for every permission the app may request. Without it, iOS silently denies the request — no dialog is shown, no error is thrown to JavaScript, the status returns as `denied` immediately.
- why_it_happens: iOS enforces that any permission a app requests must have a corresponding usage description string in Info.plist. This string appears in the permission dialog. Without the key, iOS treats the request as unauthorized and silently denies it. The JavaScript code receives `denied` as if the user refused, but no dialog was ever presented.
- accepted_fix: Add `<key>NSCameraUsageDescription</key><string>We need camera access to scan barcodes.</string>` to `ios/MyApp/Info.plist`. Rebuild the app (`pod install` then Xcode build or `npx react-native run-ios`).
- rejected_fix_patterns:
  - check device Settings app for the permission (it won't appear there either without Info.plist key)
  - uninstall and reinstall the app without adding the key
  - switch to a different camera library

## Evidence Signals

- strongest_signal: Info.plist shown in prompt does not contain NSCameraUsageDescription; permission returns denied with no dialog; Android works correctly (Android manifest separately)
- strongest_alternative_explanation: User previously denied the permission and it is remembered by iOS
- why_alternative_is_wrong: The Info.plist excerpt shows no NSCameraUsageDescription key. If the key were present but user had denied, the entry would appear in Settings > Privacy > Camera. More definitively: a fresh install with no prior permission state should show the dialog on first request if the key exists — the symptom (no dialog, instant denied) is specifically caused by missing Info.plist key.

## Scoring Notes

- full_credit_conditions:
  - identifies missing NSCameraUsageDescription in Info.plist as root cause
  - provides the exact plist key name
  - mentions rebuild requirement after plist change
- partial_credit_conditions:
  - identifies Info.plist as the problem but suggests checking device Settings first (valid secondary step but not the root cause action)
  - correct diagnosis but omits the rebuild step
- fail_conditions:
  - blames the JavaScript permission request code
  - suggests the user previously denied the permission
  - recommends switching camera library
