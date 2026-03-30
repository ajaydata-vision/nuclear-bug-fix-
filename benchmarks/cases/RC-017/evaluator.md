# Evaluator

## Metadata

- id: RC-017
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: javascript, async, parallel, shared-state, promise-all, mutation, race

## Ground Truth

- root_cause: Multiple async operations concurrently read and write result.total on a shared object. The read-modify-write is not atomic: two operations can read the same value and each add their sum, losing one update.
- why_it_happens: JavaScript is single-threaded but async operations interleave at await points. result.total += sum reads total, suspends at the next await in another task, then the original task resumes and writes back — overwriting updates made while it was suspended.
- accepted_fix: Collect results separately and aggregate after: const sums = await Promise.all(categories.map(cat => db.sumCategory(cat))); then sum sequentially. This removes the shared mutable state entirely.
- rejected_fix_patterns:
  - add a mutex/lock around the increment (over-engineered for JS)
  - reduce Promise.all concurrency to 1 (eliminates parallelism)

## Evidence Signals

- strongest_signal: Totals wrong in parallel but correct sequentially; read-modify-write on shared object across await boundaries
- strongest_alternative_explanation: Database returning wrong category sums
- why_alternative_is_wrong: Category-level values (result.categories[cat]) are always correct; only the accumulated total is wrong, pointing to the aggregation step not the DB query

## Scoring Notes

- full_credit_conditions:
  - identifies read-modify-write race across await points
  - proposes collecting results then aggregating sequentially
  - explains JavaScript async interleaving at await boundaries
- partial_credit_conditions:
  - identifies shared state issue but proposes mutex/lock
- fail_conditions:
  - reduces concurrency to 1 without explaining the root cause
  - adds error handling around the increment
