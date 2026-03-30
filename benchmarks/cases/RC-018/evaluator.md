# Evaluator

## Metadata

- id: RC-018
- domain: general
- track: deploy-env
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kubernetes, readiness, startup-race, redis, postgres

## Ground Truth

- root_cause: Readiness is reporting HTTP liveness rather than actual dependency readiness.
- why_it_happens: The pod is added to traffic before critical startup dependencies are connected.
- accepted_fix: Gate readiness on real dependency health or delay serving until startup completes.
- rejected_fix_patterns:
  - increase retries on incoming requests only
  - blame Kubernetes probe intervals alone
  - convert startup failures into ignored logs

## Evidence Signals

- strongest_signal: Readiness passes before Redis and PostgreSQL are connected
- strongest_alternative_explanation: Traffic spike overloads the pod immediately
- why_alternative_is_wrong: The failures correlate with startup order and disappear once dependencies connect

## Scoring Notes

- full_credit_conditions:
  - identifies false readiness/startup race
  - proposes real dependency-aware readiness gating
  - verification includes immediate post-readiness traffic
- partial_credit_conditions:
  - spots startup issue but suggests only delaying probe timing
- fail_conditions:
  - blames Redis outages
  - ignores the probe mismatch
