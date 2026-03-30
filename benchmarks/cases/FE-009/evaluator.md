# Evaluator

## Metadata

- id: FE-009
- domain: frontend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: websocket, race, onmessage, timing, react

## Ground Truth

- root_cause: The onmessage handler is attached asynchronously after connection opens, so messages arriving before the handler is registered are silently dropped.
- why_it_happens: WebSocket can receive messages immediately after the handshake. Attaching the handler in a setTimeout (even with delay 0) creates a gap where messages are received with no handler registered.
- accepted_fix: Attach all event handlers (onmessage, onerror, onclose) synchronously before or immediately after creating the WebSocket, before any async boundary.
- rejected_fix_patterns:
  - add retry logic for missed messages
  - add server-side buffering as only fix

## Evidence Signals

- strongest_signal: Only fast connections are affected; the race window is smaller on slow connections
- strongest_alternative_explanation: Server not sending the first message correctly
- why_alternative_is_wrong: Subsequent messages are received correctly; the issue correlates with connection speed indicating a timing gap

## Scoring Notes

- full_credit_conditions:
  - identifies handler attached after potential first message
  - proposes synchronous handler attachment
  - explains the race window
- partial_credit_conditions:
  - identifies timing issue but proposes buffering workaround only
- fail_conditions:
  - blames network instability
  - adds reconnect logic without fixing handler timing
