# Evaluator

## Metadata

- id: MO-008
- domain: frontend
- track: bohrbug-core
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, ios, background-fetch, BGAppRefreshTask, terminated

## Ground Truth

- root_cause: iOS does not permit background execution of apps that the user has explicitly force-quit from the app switcher. This is an intentional iOS OS restriction.
- why_it_happens: Force-quitting an app in iOS signals user intent to stop the app completely. iOS honours this by disabling background execution until the user manually reopens the app. Background App Refresh only applies to apps in the background state, not terminated state.
- accepted_fix: Inform users that force-quitting disables background sync, or use push notifications to wake the app instead of relying on background fetch alone.
- rejected_fix_patterns:
  - use a different minimum fetch interval
  - request higher background task priority

## Evidence Signals

- strongest_signal: Background fetch works in background state but never in terminated state; this matches documented iOS OS behavior
- strongest_alternative_explanation: Background fetch entitlement not correctly provisioned
- why_alternative_is_wrong: Background fetch works in background state confirming entitlement is correct; terminated state is an OS restriction

## Scoring Notes

- full_credit_conditions:
  - identifies iOS intentional restriction on force-quit apps
  - confirms this is expected behavior not a bug
  - proposes push notification as alternative or user education
- partial_credit_conditions:
  - correctly identifies OS restriction but does not propose alternative
- fail_conditions:
  - suggests fetching more frequently as the fix
  - blames iOS bug
