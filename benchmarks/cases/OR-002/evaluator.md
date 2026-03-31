# Evaluator

## Metadata

- id: OR-002
- domain: java-enterprise
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: hibernate, jpa, optimistic-locking, version, concurrent, retry

## Ground Truth

- root_cause: @Version enables optimistic locking — this is working as designed, not a bug. Two concurrent transactions read the same entity at version N. The first to commit succeeds and increments to N+1. The second commit fails because the version it read (N) no longer matches the current DB version (N+1). The application needs to handle this expected failure with a retry or conflict resolution strategy.
- why_it_happens: Optimistic locking detects write-write conflicts at commit time. It is designed to prevent lost updates (silent overwrites). The exception is the correct behavior — the application must decide what to do: retry, merge, or surface a conflict error to the user.
- accepted_fix: Add retry logic at the service layer using @Retryable(ObjectOptimisticLockingFailureException.class). Or for highly-contended resources, switch to pessimistic locking (SELECT FOR UPDATE) to serialize access. Or surface the conflict to the user with a 409 Conflict response.
- rejected_fix_patterns:
  - remove @Version field (disables conflict detection — loses updates silently)
  - catch the exception and ignore it (lost update — second write is silently discarded)

## Evidence Signals

- strongest_signal: ObjectOptimisticLockingFailureException on concurrent update of same order; @Version field present; single-user never fails; concurrent users both start at same version
- strongest_alternative_explanation: Hibernate bug causing incorrect version comparison
- why_alternative_is_wrong: This is the exact documented behavior of @Version optimistic locking per JPA specification. The exception message explicitly states "Row was updated by another transaction" — this is expected, not erroneous.

## Scoring Notes

- full_credit_conditions:
  - identifies this as expected optimistic locking behavior (not a bug in Hibernate)
  - explains read-modify-commit conflict at the version level
  - proposes retry or pessimistic locking as the application-level fix
- partial_credit_conditions:
  - identifies the exception correctly but recommends removing @Version as fix
- fail_conditions:
  - blames PostgreSQL transaction isolation
  - suggests this is a Hibernate bug requiring upgrade
