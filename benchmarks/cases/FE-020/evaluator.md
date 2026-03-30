# Evaluator

## Metadata

- id: FE-020
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: firefox, date-parsing, cross-browser, invalid-date, ISO8601

## Ground Truth

- root_cause: The date string uses a space separator instead of T between date and time. Chrome parses this leniently but Firefox strictly follows the ISO 8601 spec which requires T.
- why_it_happens: The ECMAScript spec defines ISO 8601 date format with T as the date-time separator. '2024-01-15 09:30:00' with a space is not valid ISO 8601 and Firefox rejects it. Chrome's V8 parses it leniently as an extension.
- accepted_fix: Replace the space with T before parsing: new Date(dateString.replace(' ', 'T')) or use a date library like date-fns that handles multiple formats.
- rejected_fix_patterns:
  - add Firefox-specific polyfill
  - change API to return timestamps

## Evidence Signals

- strongest_signal: Exact same string parses in Chrome but returns Invalid Date in Firefox; string uses space not T
- strongest_alternative_explanation: Firefox locale setting affecting date parsing
- why_alternative_is_wrong: Locale affects formatting not parsing; the Invalid Date is returned before any formatting

## Scoring Notes

- full_credit_conditions:
  - identifies space vs T separator as the spec violation
  - proposes .replace() or date library
  - explains lenient vs strict parsing difference
- partial_credit_conditions:
  - identifies cross-browser date issue but not the specific character
- fail_conditions:
  - adds Firefox-only code path
  - changes API response format without explaining why the current format is problematic
