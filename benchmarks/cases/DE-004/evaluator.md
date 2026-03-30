# Evaluator

## Metadata

- id: DE-004
- domain: general
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: migration, schema, column-missing, deploy, prisma, sequelize

## Ground Truth

- root_cause: The database migration adding the new column was not run after deployment, leaving the production schema behind the application code.
- why_it_happens: Application code references schema changes that only exist in migration files. The migration must be applied to the database for the code to work.
- accepted_fix: Run npx prisma migrate deploy as part of the deploy script before restarting the application. Never restart the app before the schema matches the code.
- rejected_fix_patterns:
  - manually add the column in production without running the migration
  - rollback the code to before the migration

## Evidence Signals

- strongest_signal: prisma migrate status shows pending migration; production DB missing the column that code references
- strongest_alternative_explanation: Wrong database connection string pointing to another DB
- why_alternative_is_wrong: Other queries work correctly; the specific missing column is the only failure, matching the pending migration content

## Scoring Notes

- full_credit_conditions:
  - identifies migration not run after deploy
  - proposes adding migrate deploy to deploy script before app restart
  - explains code-schema synchronization requirement
- partial_credit_conditions:
  - identifies the missing migration but proposes only running it manually this time
- fail_conditions:
  - adds the column manually without the migration
  - blames Prisma migration system
