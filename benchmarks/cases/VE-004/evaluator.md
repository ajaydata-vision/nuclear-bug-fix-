# Evaluator

## Metadata

- id: VE-004
- domain: version-external-intelligence
- track: regression-version
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: chrome, deprecated-api, browser-update, geolocation, breaking-change

## Ground Truth

- root_cause: Chrome 121 removed the Vibration API on non-mobile platforms (desktop Chrome). The API was deprecated in Chrome 120 and removed in 121.
- why_it_happens: Google removed Vibration API on desktop Chrome because desktop devices rarely have vibration hardware. The deprecation warning in Chrome 120 was the signal before removal.
- accepted_fix: Check for support before calling: if (navigator.vibrate) { navigator.vibrate(200) }. Accept that desktop Chrome users will not receive haptic feedback.
- rejected_fix_patterns:
  - polyfill the Vibration API on desktop
  - show error to users when vibrate is unavailable

## Evidence Signals

- strongest_signal: Feature stopped working after Chrome update; deprecation warning preceded the removal; only desktop Chrome affected
- strongest_alternative_explanation: Permission denied for vibration
- why_alternative_is_wrong: Vibration API does not require permissions; the function returning false indicates absence not denial

## Scoring Notes

- full_credit_conditions:
  - identifies Chrome 121 Vibration API removal on desktop
  - proposes feature detection before calling
  - references MDN/Chrome release notes
- partial_credit_conditions:
  - identifies browser removal but does not propose feature detection
- fail_conditions:
  - suggests polyfilling the removed API
  - recommends reverting Chrome
