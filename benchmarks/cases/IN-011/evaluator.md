# Evaluator

## Metadata

- id: IN-011
- domain: integration
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: event-bus, topic, sns, eventbridge, mismatch, publish-subscribe

## Ground Truth

- root_cause: The EventBridge rule pattern uses a different source string than what the publisher sends, so no events match the rule.
- why_it_happens: EventBridge routing is based on exact pattern matching of event fields. A one-character difference in the source string means zero events are routed to that rule.
- accepted_fix: Fix the typo in the consumer rule pattern to match 'com.example.orders'. Or use a shared constant for event sources to prevent future mismatches.
- rejected_fix_patterns:
  - change the publisher to use the wrong source string to match the typo
  - add a catch-all rule

## Evidence Signals

- strongest_signal: Zero matched rules in EventBridge despite successful publish; typo visible in rule pattern vs published event source
- strongest_alternative_explanation: EventBridge target Lambda has permissions error
- why_alternative_is_wrong: Lambda is never invoked; the rule itself matches zero events proving the issue is the pattern not the target

## Scoring Notes

- full_credit_conditions:
  - identifies source string typo in rule pattern
  - proposes fixing the rule and using shared constants
  - confirms by checking EventBridge matched rule count
- partial_credit_conditions:
  - identifies the mismatch but does not recommend constants to prevent recurrence
- fail_conditions:
  - changes publisher source to match the wrong rule string
  - checks Lambda permissions before the rule
