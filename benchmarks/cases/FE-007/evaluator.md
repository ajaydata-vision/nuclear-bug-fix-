# Evaluator

## Metadata

- id: FE-007
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: json, serialization, date, type-coercion, api

## Ground Truth

- root_cause: The frontend sends dueDate as a Unix timestamp in milliseconds, but the API expects an ISO 8601 string.
- why_it_happens: Date.getTime() returns a number (ms since epoch). The backend schema validates against an ISO 8601 format string and rejects a numeric value.
- accepted_fix: Serialize the date as an ISO string: selectedDate.toISOString()
- rejected_fix_patterns:
  - change backend to accept timestamps without aligning with the API contract
  - add frontend error suppression

## Evidence Signals

- strongest_signal: Network tab shows a number for the date field; backend error explicitly says it expected ISO 8601
- strongest_alternative_explanation: Backend validation bug
- why_alternative_is_wrong: The backend error message explicitly states the format it received versus expected; the problem is the frontend serialization

## Scoring Notes

- full_credit_conditions:
  - identifies getTime() returning milliseconds
  - proposes toISOString()
  - explains the format mismatch
- partial_credit_conditions:
  - identifies date format mismatch but proposes changing backend schema
- fail_conditions:
  - adds frontend try/catch without fixing format
  - blames backend validation as wrong
