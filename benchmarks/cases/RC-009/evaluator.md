# Evaluator

## Metadata

- id: RC-009
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: migration, race, concurrent-deploy, advisory-lock, schema

## Ground Truth

- root_cause: Multiple pods run database migrations concurrently during rolling deployment with no mutual exclusion, causing the same migration to be applied multiple times.
- why_it_happens: Without a distributed lock, any pod that starts during a rolling deploy may run migrations before seeing them as already applied by another pod (race in the migration status check).
- accepted_fix: Use a Kubernetes init container or a separate pre-deploy job to run migrations exactly once before pods start. Or use PostgreSQL advisory locks in the migration runner to ensure only one instance runs at a time.
- rejected_fix_patterns:
  - set deployment strategy to Recreate (causes downtime)
  - run migrations manually before every deploy

## Evidence Signals

- strongest_signal: Migration table shows same migration twice; timing correlates with rolling deploy overlap window
- strongest_alternative_explanation: Prisma migration bug
- why_alternative_is_wrong: The migration ran correctly; the issue is running it twice due to concurrent pod startup

## Scoring Notes

- full_credit_conditions:
  - identifies concurrent migration from multiple pods
  - proposes init container or advisory lock
  - explains rolling deploy overlap window
- partial_credit_conditions:
  - identifies the race but proposes Recreate strategy as the fix
- fail_conditions:
  - blames Prisma migration system
  - manually reverts the migration without preventing recurrence
