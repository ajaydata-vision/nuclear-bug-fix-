# Evaluator

## Metadata

- id: JV-007
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: nio, selector, selectedkeys, cancelledkeyexception, iterator, remove

## Ground Truth

- root_cause: The selectedKeys set is iterated with a for-each loop but keys are never removed after processing. The JDK adds keys to selectedKeys but never removes them automatically. On the next selector.select() call, the previously cancelled key remains in the set. Processing it throws CancelledKeyException.
- why_it_happens: selector.selectedKeys() returns a live Set that only grows. The JDK contract requires the developer to remove keys from selectedKeys after processing them — typically by using Iterator.remove() inside the loop. Without removal, cancelled or stale keys persist in the set across select() iterations.
- accepted_fix: Use Iterator<SelectionKey> with iter.remove() after each key is processed. Also add key.isValid() check before processing to guard against keys cancelled by other means.
- rejected_fix_patterns:
  - clear the entire selectedKeys set after the loop (keys.clear()) — works but misses keys added during processing in multi-threaded scenarios; iterator approach is canonical
  - catch CancelledKeyException inside the loop (masks the bug, does not fix stale key accumulation)

## Evidence Signals

- strongest_signal: for-each loop on selectedKeys with no Iterator.remove(); CancelledKeyException on second select() iteration after a disconnect; key.cancel() called in catch block
- strongest_alternative_explanation: key.cancel() called multiple times for the same key (double-cancel)
- why_alternative_is_wrong: double-cancel does not throw CancelledKeyException — it is idempotent. The exception is thrown when trying to USE a cancelled key (check isReadable() etc.), which happens because the cancelled key was never removed from selectedKeys

## Scoring Notes

- full_credit_conditions:
  - identifies missing Iterator.remove() as root cause
  - explains JDK never removes keys from selectedKeys automatically
  - proposes Iterator<SelectionKey> with iter.remove()
- partial_credit_conditions:
  - suggests keys.clear() after loop (functional workaround, not canonical fix)
  - suggests catching CancelledKeyException without fixing removal
- fail_conditions:
  - blames key.cancel() as the problem
  - suggests not cancelling keys on disconnect
