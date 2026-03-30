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
- tags: javascript, async, parallel, shared-state, promise-all, stale-snapshot, race

## Ground Truth

- root_cause: Each async task snapshots result.total into currentTotal, then awaits audit.logCategoryTotal before writing result.total = currentTotal + sum. Other tasks can update result.total during that await, so the stale snapshot overwrites newer totals.
- why_it_happens: JavaScript is single-threaded, but async continuations resume between await points. The stale snapshot crosses an await boundary, so later writes are based on old state rather than the latest accumulated total.
- accepted_fix: Return per-category results from each task, then aggregate after Promise.all resolves. For example: const rows = await Promise.all(categories.map(async cat => ({ cat, sum: await db.sumCategory(cat) }))); then sum rows sequentially into result.total and result.categories. This removes the stale shared-state write.
- rejected_fix_patterns:
  - add a mutex/lock around the increment (over-engineered for JS)
  - reduce Promise.all concurrency to 1 (eliminates parallelism)

## Evidence Signals

- strongest_signal: Totals are wrong only when the extra async audit step is enabled; the stale currentTotal snapshot crosses an await boundary before writing back
- strongest_alternative_explanation: Database returning wrong category sums
- why_alternative_is_wrong: Category-level values (result.categories[cat]) are always correct; only the accumulated total is wrong, pointing to the aggregation step rather than the DB query

## Scoring Notes

- full_credit_conditions:
  - identifies the stale total snapshot crossing an await boundary
  - proposes collecting results then aggregating sequentially
  - explains JavaScript async interleaving at await boundaries
- partial_credit_conditions:
  - identifies shared state issue but proposes mutex/lock
- fail_conditions:
  - claims plain result.total += sum is itself the race without the await gap
  - reduces concurrency to 1 without explaining the root cause
  - adds error handling around the increment
