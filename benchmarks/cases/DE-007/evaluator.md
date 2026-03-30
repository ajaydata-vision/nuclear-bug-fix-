# Evaluator

## Metadata

- id: DE-007
- domain: general
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: deploy, environment, staging, production, misconfiguration, env-flag

## Ground Truth

- root_cause: The deploy script runs without specifying the production environment flag, defaulting to staging.
- why_it_happens: The deploy script uses a default environment (staging) when no --env flag is provided. The CI workflow for main branch merges does not pass --env production.
- accepted_fix: Add --env production to the deploy command in the CI workflow for the production deployment step.
- rejected_fix_patterns:
  - manually deploy to production after CI
  - disable staging deploy

## Evidence Signals

- strongest_signal: CI log shows deploy target: staging; only staging is updated; missing environment flag in CI config
- strongest_alternative_explanation: Production environment locked during business hours
- why_alternative_is_wrong: The CI log explicitly shows the wrong target environment; the deploy succeeded to the wrong place

## Scoring Notes

- full_credit_conditions:
  - identifies missing --env production flag in CI
  - proposes adding the flag to the workflow
  - confirms by checking CI deploy target in logs
- partial_credit_conditions:
  - identifies wrong environment deployed but does not pinpoint the missing flag
- fail_conditions:
  - re-runs the deployment manually without fixing CI
  - blames CI platform
