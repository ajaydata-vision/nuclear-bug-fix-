# Evaluator

## Metadata

- id: BI-002
- domain: bridge-adapters
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: reconnect, duplicate-listener, baileys, event-emitter, websocket

## Ground Truth

- root_cause: Reconnect recreates bridge wiring without tearing down old listeners, so `messages.upsert` handlers accumulate across reconnect cycles and the same message is forwarded multiple times.
- why_it_happens: Each reconnect creates a fresh socket/listener graph. Without explicit teardown or one-time registration discipline, the process retains multiple active handlers.
- accepted_fix: Ensure old listeners/sockets are disposed before reconnect, or centralize listener registration so each lifecycle has exactly one `messages.upsert` handler.
- rejected_fix_patterns:
  - deduplicate only in the database/UI while keeping duplicate handlers
  - restart the whole app as the main fix
  - increase reconnect timeout without fixing listener lifecycle

## Evidence Signals

- strongest_signal: Duplicate count grows with reconnect count, and handler registration lives inside reconnect logic.
- strongest_alternative_explanation: WhatsApp itself redelivers the same message multiple times after reconnect.
- why_alternative_is_wrong: Delivery count scales with reconnect cycles and local handler registration structure, which matches listener accumulation rather than protocol redelivery.

## Scoring Notes

- full_credit_conditions:
  - identifies listener accumulation across reconnects
  - explains why duplicate count grows with each reconnect
  - fixes by disposing old listeners or guaranteeing exactly one handler per lifecycle
- partial_credit_conditions:
  - identifies reconnect duplication but proposes only downstream dedupe
- fail_conditions:
  - blames WhatsApp servers without local lifecycle evidence
  - suggests increasing reconnect delay only
  - blames Python UI rendering
