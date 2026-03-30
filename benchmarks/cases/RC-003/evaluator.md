# Evaluator

## Metadata

- id: RC-003
- domain: backend
- track: bohrbug-core
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: double-submit, idempotency, form, race, button

## Ground Truth

- root_cause: The button is not disabled during submission, allowing multiple clicks to fire multiple requests, and the backend has no idempotency guard against duplicate submits.
- why_it_happens: Defense in depth is required: frontend prevents accidental double-clicks; backend prevents any duplicate that slips through (from double-click, retry, or race).
- accepted_fix: Frontend: disable the button during submission and re-enable on completion/error. Backend: use an idempotency key (client-generated UUID) with a unique DB constraint to reject true duplicates.
- rejected_fix_patterns:
  - add debounce only (does not protect against intentional or network-level retries)
  - add only a backend check without the frontend guard

## Evidence Signals

- strongest_signal: Two identical POST requests arrive within milliseconds; button not disabled during submission
- strongest_alternative_explanation: Browser sending requests multiple times due to timeout
- why_alternative_is_wrong: The timing (milliseconds apart) matches double-click not browser timeout retry (which would be seconds apart)

## Scoring Notes

- full_credit_conditions:
  - disables button during submission
  - adds backend idempotency key with unique constraint
  - explains both layers of defense needed
- partial_credit_conditions:
  - fixes only frontend or only backend without explaining why both are needed
- fail_conditions:
  - adds debounce as the primary fix
  - blames user behavior without providing a technical fix
