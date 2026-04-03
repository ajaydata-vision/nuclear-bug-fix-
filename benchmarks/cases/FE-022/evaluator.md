# Evaluator

## Metadata

- id: FE-022
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: javascript, async, forEach, await, promise, batch-processing

## Ground Truth

- root_cause: `Array.prototype.forEach` does not await promises returned by its async callback. `forEach` fires all 47 async callbacks simultaneously and returns `undefined` immediately — it has no mechanism to wait for promises. `await users.forEach(...)` is a no-op: `await undefined` completes instantly. The code after the loop runs before any save completes, logging "0 saved".
- why_it_happens: `forEach` was designed before async/await existed. It invokes each callback synchronously and discards any return value — including returned promises. The inner `await apiClient.saveUser(user)` awaits correctly inside the callback's own execution context, but `forEach` itself does not wait for those callbacks to finish. The outer `await` on `forEach` has nothing to await (forEach returns `undefined`), so it resolves instantly.
- accepted_fix: Replace `forEach` with `for...of` to await each save sequentially, OR use `Promise.all(users.map(...))` to await all saves in parallel with proper tracking.
- rejected_fix_patterns:
  - add `.then()` chain after forEach
  - increase a timeout before the completion log
  - use `Array.prototype.map` without `Promise.all` (same problem — map also ignores async callbacks)

## Evidence Signals

- strongest_signal: "Import complete: 0 saved" appears immediately before any save confirmations; saves arrive 2-3 seconds later out of order; code uses `await users.forEach(async ...)` pattern; `savedCount` is 0 because increments happen after forEach returns
- strongest_alternative_explanation: `apiClient.saveUser` is not returning a promise and the await is consuming a non-promise value
- why_alternative_is_wrong: Save confirmations DO arrive eventually (all 47 complete), proving `apiClient.saveUser` returns a working promise. The issue is that forEach does not wait for those promises — if saveUser returned a non-promise, the saves would never complete at all.

## Scoring Notes

- full_credit_conditions:
  - identifies forEach not awaiting async callbacks as root cause
  - explains that await on forEach is a no-op (forEach returns undefined)
  - prescribes for...of loop OR Promise.all with map
- partial_credit_conditions:
  - correctly identifies the forEach problem but only prescribes for...of without mentioning Promise.all as an option for parallel execution
  - prescribes Promise.all correctly but does not explain why forEach specifically is wrong
- fail_conditions:
  - suggests adding .then() after forEach
  - recommends increasing a timeout
  - blames apiClient.saveUser implementation
