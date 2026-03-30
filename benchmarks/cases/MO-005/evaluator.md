# Evaluator

## Metadata

- id: MO-005
- domain: mobile
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, offline-sync, reconnect, queue, netinfo

## Ground Truth

- root_cause: Reconnect does not trigger the pending sync path while the app remains alive.
- why_it_happens: Pending writes are persisted, but there is no listener or trigger wiring `syncPending()` to network restoration.
- accepted_fix: Subscribe to connectivity changes and flush the queue on reconnect, with dedupe and failure handling.
- rejected_fix_patterns:
  - rely on app restart only
  - blame AsyncStorage corruption
  - run sync continuously in a tight loop

## Evidence Signals

- strongest_signal: Relaunch triggers successful sync, proving the queue data itself is intact
- strongest_alternative_explanation: The queue never saved the changes
- why_alternative_is_wrong: The offline data survives and syncs correctly after restart

## Scoring Notes

- full_credit_conditions:
  - identifies missing reconnect trigger
  - proposes NetInfo or equivalent reconnect listener
  - verification includes airplane-mode reconnect flow
- partial_credit_conditions:
  - identifies lifecycle issue but not the exact reconnect event
- fail_conditions:
  - blames server sync endpoint only
  - ignores the successful post-restart flush clue
