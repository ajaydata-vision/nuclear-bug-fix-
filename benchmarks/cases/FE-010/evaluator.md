# Evaluator

## Metadata

- id: FE-010
- domain: frontend
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: websocket, reconnect, close-code, auth, infinite-loop

## Ground Truth

- root_cause: The reconnect logic does not inspect the close code, so auth failures (code 4001) trigger the same reconnect as network drops, creating an infinite loop.
- why_it_happens: Close codes communicate the reason for disconnection. Code 4001 is an application-level auth error that cannot be resolved by reconnecting. The fix must check the code and only reconnect on recoverable errors.
- accepted_fix: Check ws.onclose event.code: only reconnect on codes that indicate recoverable network issues (1001, 1006) and handle auth errors (4001) by redirecting to login.
- rejected_fix_patterns:
  - add exponential backoff without checking close code
  - disable auto-reconnect entirely

## Evidence Signals

- strongest_signal: Every reconnect immediately closes with the same 4001 code; backoff would not help
- strongest_alternative_explanation: Server bug sending wrong close code
- why_alternative_is_wrong: Code 4001 is consistently sent on auth expiry as designed; the client must handle it correctly

## Scoring Notes

- full_credit_conditions:
  - identifies missing close code inspection
  - proposes checking code before reconnecting
  - handles auth error appropriately
- partial_credit_conditions:
  - adds backoff but does not check close code
- fail_conditions:
  - suggests disabling auto-reconnect entirely
  - blames server for not staying connected
