# Evaluator

## Metadata

- id: FE-016
- domain: frontend
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: localStorage, private-browsing, safari, storage, error-handling

## Ground Truth

- root_cause: Safari in private browsing mode throws a SecurityError on any localStorage write, even though the API appears available. Other browsers allow limited localStorage in private mode.
- why_it_happens: Safari intentionally blocks localStorage writes in private mode as a privacy measure. The API is present but throws when used, unlike Chrome which allows it with a size limit.
- accepted_fix: Wrap localStorage access in try/catch and fall back to sessionStorage or in-memory storage when the write fails.
- rejected_fix_patterns:
  - detect private browsing mode by checking quota
  - force users to leave private mode

## Evidence Signals

- strongest_signal: Error only in Safari private mode; other browsers work; error is thrown on write not on read
- strongest_alternative_explanation: Storage quota exceeded
- why_alternative_is_wrong: Quota errors produce QuotaExceededError not SecurityError; the login data is small

## Scoring Notes

- full_credit_conditions:
  - identifies Safari private mode blocking localStorage writes
  - proposes try/catch with sessionStorage fallback
  - explains cross-browser behavior difference
- partial_credit_conditions:
  - identifies storage error but does not address the fallback
- fail_conditions:
  - blocks Safari users from using the app
  - detects private mode without providing fallback
