# Evaluator

## Metadata

- id: RC-005
- domain: backend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: websocket, race, http, state, ordering, real-time

## Ground Truth

- root_cause: The WebSocket broadcast fires before the HTTP response is sent. On fast networks, other clients receive the update event before the originating client confirms the HTTP save.
- why_it_happens: Event ordering matters in collaborative systems. The originating client must confirm the save before receiving the broadcast, otherwise it may process the WS event as a conflicting update.
- accepted_fix: Emit the WebSocket broadcast after sending the HTTP response, or emit it only to other clients (exclude the socket of the requester until the HTTP response is acknowledged).
- rejected_fix_patterns:
  - add a client-side delay before processing WS events
  - disable WS events for the originating client

## Evidence Signals

- strongest_signal: Race is timing-dependent; WS event arrives before HTTP response on fast networks; reordering emit after res.json eliminates the issue
- strongest_alternative_explanation: HTTP request taking too long before the WS event arrives
- why_alternative_is_wrong: The WS event is emitted on the server before res.json() is called; the ordering is deterministic in the server code

## Scoring Notes

- full_credit_conditions:
  - identifies emit before res.json() as the ordering problem
  - proposes emitting after res.json() or broadcasting to other clients only
  - explains collaborative state ordering requirement
- partial_credit_conditions:
  - identifies the race but proposes only client-side mitigation
- fail_conditions:
  - adds retry logic on the client
  - blames WebSocket library
