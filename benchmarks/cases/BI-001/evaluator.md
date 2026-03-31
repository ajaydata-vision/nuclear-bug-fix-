# Evaluator

## Metadata

- id: BI-001
- domain: bridge-adapters
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: true
- requires_log_access: true
- tags: handshake, startup-race, whatsapp, baileys, websocket, bridge

## Ground Truth

- root_cause: The parent treats subprocess spawn as readiness and attaches the bridge reader too late. The child emits its first inbound event after `bridge_ready` but before the parent listener is fully attached, so the first message is lost.
- why_it_happens: Spawned process != ready protocol. Bridge startup has at least three states: child process exists, child authenticated/ready, parent listener attached. Early events emitted between those states are dropped.
- accepted_fix: Introduce an explicit ready handshake and do not mark connected until the parent listener is attached and the child has declared ready. Buffer or replay early events if needed.
- rejected_fix_patterns:
  - add arbitrary startup sleeps
  - retry UI rendering without fixing the readiness contract
  - mark bridge connected at process spawn time

## Evidence Signals

- strongest_signal: Timeline shows parent listener attach after child ready and after the first `messages.upsert`.
- strongest_alternative_explanation: First message is filtered or deduplicated by the UI layer.
- why_alternative_is_wrong: The child log already shows the event occurred before the parent listener existed. The loss happens at the bridge boundary, not the UI.

## Scoring Notes

- full_credit_conditions:
  - identifies process-spawn vs bridge-ready vs listener-attached as separate states
  - points to the first-event ordering race from the timestamps
  - fixes with explicit handshake/buffering before declaring connected
- partial_credit_conditions:
  - identifies a startup race but proposes only sleeps without a readiness contract
- fail_conditions:
  - blames Baileys message deduplication without timeline proof
  - blames websocket packet loss
  - suggests polling for new messages instead of fixing startup ordering
