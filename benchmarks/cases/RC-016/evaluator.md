# Evaluator

## Metadata

- id: RC-016
- domain: frontend
- track: intermittent-race
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: websocket, reconnect, event-listener, duplicate, accumulation, react

## Ground Truth

- root_cause: Each reconnect creates a new WebSocket instance with a new handler, but the previous WebSocket's handlers are not removed. If the old connection is still partially open, both process messages.
- why_it_happens: Assigning ws.onmessage replaces the handler on that specific WebSocket instance. A new WebSocket object has no reference to the previous instance's cleanup. Both instances can receive and handle the same message.
- accepted_fix: Close the previous WebSocket explicitly before reconnecting: if (ws) { ws.onmessage = null; ws.onclose = null; ws.close(); } then create the new WebSocket.
- rejected_fix_patterns:
  - deduplicate notifications by message ID on the UI (symptom fix, not root fix)
  - add a global flag to prevent multiple handlers

## Evidence Signals

- strongest_signal: Duplicate count equals reconnect cycle count; old WebSocket instance not explicitly closed before creating new one
- strongest_alternative_explanation: Server sending duplicate messages
- why_alternative_is_wrong: Server sends each message once; the client processes it N times because N WebSocket instances are active simultaneously

## Scoring Notes

- full_credit_conditions:
  - identifies old WebSocket not closed before reconnect
  - proposes null handlers and ws.close() before recreating
  - explains why multiple instances coexist
- partial_credit_conditions:
  - deduplicates on the UI without closing the old connection
- fail_conditions:
  - adds message ID deduplication as the complete fix
  - blames server for duplicate sends
