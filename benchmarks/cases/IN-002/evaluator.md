# Evaluator

## Metadata

- id: IN-002
- domain: integration
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: webhook, signature, raw-body, express, payments

## Ground Truth

- root_cause: Signature verification is performed on re-serialized JSON instead of the original raw request bytes.
- why_it_happens: `express.json()` consumes and transforms the body before the signature check.
- accepted_fix: Capture and verify the raw body before JSON parsing for this route.
- rejected_fix_patterns:
  - rotate the secret
  - trim whitespace in the secret only
  - skip signature verification in production

## Evidence Signals

- strongest_signal: Webhook reaches the endpoint but signature mismatches 100% of the time despite correct secret
- strongest_alternative_explanation: Provider is signing with the wrong secret
- why_alternative_is_wrong: The failure is deterministic and aligned with a body-transformation bug in the endpoint implementation

## Scoring Notes

- full_credit_conditions:
  - identifies raw-body preservation as the cause
  - proposes route-level raw parser or body capture before parsing
  - verification includes replaying a real signed webhook
- partial_credit_conditions:
  - spots middleware ordering issue but does not mention raw bytes
- fail_conditions:
  - blames provider outage
  - disables signature validation
