# Evaluator

## Metadata

- id: BE-009
- domain: backend
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: race, postgres, unique-constraint, toctou, signup

## Ground Truth

- root_cause: The code uses a check-then-insert pattern, creating a TOCTOU race.
- why_it_happens: Two requests both observe "no user exists" before either insert commits.
- accepted_fix: Use an atomic insert/upsert pattern and treat the database constraint as the final guard.
- rejected_fix_patterns:
  - keep the pre-check and add sleep
  - disable the unique constraint
  - blame SQLAlchemy session caching

## Evidence Signals

- strongest_signal: Both requests pass the pre-check before one fails on insert
- strongest_alternative_explanation: The ORM duplicates a single request internally
- why_alternative_is_wrong: The failure occurs only with concurrent requests for the same key

## Scoring Notes

- full_credit_conditions:
  - identifies TOCTOU race
  - proposes upsert or insert-and-handle-conflict
  - verification includes concurrent duplicate signup
- partial_credit_conditions:
  - spots concurrency issue but proposes locking the whole app broadly
- fail_conditions:
  - removes the unique constraint
  - keeps application pre-check as sole protection
