# Evaluator

## Metadata

- id: PD-005
- domain: python-desktop
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: sqlite, aiosqlite, transaction, qasync, background-sync, ui-write

## Ground Truth

- root_cause: The app shares one SQLite connection across overlapping UI and
  background write paths, and the sync path holds a transaction open while
  another write tries to use the same database file.
- why_it_happens: SQLite allows only limited concurrent writing. A long-lived
  write transaction or overlapping commits will contend for the same lock and
  surface as `database is locked`.
- accepted_fix: Serialize writes through a single queue or short-lived
  transaction boundary, avoid holding the write lock across unrelated async
  work, and isolate read/write access patterns appropriately.
- rejected_fix_patterns:
  - retry the same write forever
  - turn off thread checks or ignore lock errors
  - move the database file without fixing the transaction overlap

## Evidence Signals

- strongest_signal: The lock error only appears when UI writes overlap with a
  background sync transaction, and the logs show the commit boundary has not
  completed yet.
- strongest_alternative_explanation: The database file is corrupted.
- why_alternative_is_wrong: The error timing matches overlapping writes, not a
  corrupt file, and the app recovers when the write overlap does not occur.

## Scoring Notes

- full_credit_conditions:
  - identifies overlapping SQLite writes/transactions as the cause
  - explains that the lock comes from concurrent access, not corruption
  - fixes by serializing writes or shortening the transaction window
- partial_credit_conditions:
  - identifies concurrency but suggests only generic retry logic
- fail_conditions:
  - blames schema migration
  - suggests increasing the SQLite timeout as the only fix
  - ignores the overlapping commit window
