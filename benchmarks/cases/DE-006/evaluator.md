# Evaluator

## Metadata

- id: DE-006
- domain: general
- track: deploy-env
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: partial-rollout, load-balancer, version-skew, sentinel, deploy

## Ground Truth

- root_cause: The environment is serving mixed versions because one instance was not updated during rollout.
- why_it_happens: Requests routed to the stale instance still execute the old buggy code path.
- accepted_fix: Remove the old instance from rotation and enforce all-instance version verification during deploy.
- rejected_fix_patterns:
  - keep debugging the app logic only
  - blame nondeterministic race conditions first
  - treat intermittent behavior as proof the fix is bad

## Evidence Signals

- strongest_signal: Request failures correlate exactly with the one instance missing the new version or sentinel
- strongest_alternative_explanation: The fix itself is flaky across all instances
- why_alternative_is_wrong: New instances behave consistently while only the stale instance reproduces the old bug

## Scoring Notes

- full_credit_conditions:
  - identifies partial rollout / version skew
  - proposes instance-level version verification and full replacement
  - verification includes checking all instances, not just one
- partial_credit_conditions:
  - spots rollout issue but does not require all-instance verification
- fail_conditions:
  - keeps analyzing source logic without resolving the old node
  - blames random race conditions
