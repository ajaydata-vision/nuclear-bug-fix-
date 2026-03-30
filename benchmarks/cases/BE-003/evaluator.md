# Evaluator

## Metadata

- id: BE-003
- domain: backend
- track: distributed-multi-factor
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: idempotency, retries, duplicate-write, api, postgres

## Ground Truth

- root_cause: The create endpoint is not idempotent, so legitimate retries create duplicate side effects.
- why_it_happens: The same semantic operation is executed twice and nothing deduplicates or guards it.
- accepted_fix: Use an idempotency key or another unique semantic constraint so retried requests resolve to the same operation.
- rejected_fix_patterns:
  - add client-side debounce only
  - assume frontend double-click is the only cause
  - send email after response without deduping the order write

## Evidence Signals

- strongest_signal: Duplicate orders share the same payload and happen near timeout/retry windows
- strongest_alternative_explanation: The route handler is mounted twice
- why_alternative_is_wrong: Duplicate requests are visible independently and both are accepted as valid creates

## Scoring Notes

- full_credit_conditions:
  - names retry-induced duplicate processing
  - proposes idempotency key or unique semantic guard
  - verification includes same payload replay
- partial_credit_conditions:
  - mentions retries but proposes only a frontend fix
- fail_conditions:
  - blames PostgreSQL consistency
  - ignores duplicate side effects
