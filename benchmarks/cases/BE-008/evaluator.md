# Evaluator

## Metadata

- id: BE-008
- domain: backend
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: migration, database, connection-string, env-var, staging, wrong-db

## Ground Truth

- root_cause: The migration ran against the staging database because the local .env file's DATABASE_URL points to staging, overriding the production connection string.
- why_it_happens: Prisma uses DATABASE_URL to determine which database to migrate. The local .env file took precedence over the intended production target. Migration succeeded on staging, not production.
- accepted_fix: Run production migrations only through CI/CD using the production DATABASE_URL from the secret vault, never locally with a .env override. Add a pre-migration check that logs the database host before applying.
- rejected_fix_patterns:
  - re-run migration locally after fixing .env
  - add a confirmation prompt to the migration script

## Evidence Signals

- strongest_signal: Migration logs show success but production schema unchanged; staging has the new column; DATABASE_URL in .env points to staging host
- strongest_alternative_explanation: Migration applied but rolled back by PostgreSQL
- why_alternative_is_wrong: PostgreSQL would log a rollback; staging has the column confirming the migration ran — just against the wrong target

## Scoring Notes

- full_credit_conditions:
  - identifies wrong DATABASE_URL pointing to staging
  - proposes CI/CD-only migrations with production secrets
  - recommends pre-migration host logging
- partial_credit_conditions:
  - identifies wrong DB but only proposes fixing .env without addressing the process gap
- fail_conditions:
  - reruns the migration without verifying the target DB
  - blames Prisma for running against wrong DB
