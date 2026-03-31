# Evaluator

## Metadata

- id: BI-005
- domain: bridge-adapters
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: true
- requires_log_access: true
- tags: websocket, listener-ordering, startup-race, bridge, event-loss

## Ground Truth

- root_cause: The bridge emits the first realtime event before the downstream
  listener is attached, so the initial message is lost during startup ordering.
- why_it_happens: Process spawn and child readiness are not the same as listener
  attachment. On slower startups, the child can emit before the parent is ready
  to consume.
- accepted_fix: Attach listeners before declaring ready, or buffer/replay early
  events until the listener is fully attached and the handshake is complete.
- rejected_fix_patterns:
  - add sleeps around startup
  - reconnect to recover a message that was never listened for
  - duplicate listeners to "catch" the event

## Evidence Signals

- strongest_signal: Timestamps show the child emitted the first event before the
  parent listener was attached.
- strongest_alternative_explanation: WhatsApp dropped the first message.
- why_alternative_is_wrong: The local timeline already proves the bridge missed
  the event before it left the child process boundary.

## Scoring Notes

- full_credit_conditions:
  - identifies the listener-attachment race
  - explains why the first event is specifically lost
  - fixes by ordering listener registration before emission or buffering early events
- partial_credit_conditions:
  - identifies a race but only suggests sleeps
- fail_conditions:
  - blames WhatsApp network delivery
  - suggests downstream dedupe as the fix
  - ignores the startup ordering problem
