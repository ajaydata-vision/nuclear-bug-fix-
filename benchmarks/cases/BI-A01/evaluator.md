# Evaluator

## Metadata

- id: BI-A01
- domain: bridge-adapters
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: stdout, json, protocol, bridge, baileys, node-python

## Ground Truth

- root_cause: The child uses stdout as a JSON protocol channel but also writes human-readable debug logs to stdout with `console.log`, corrupting the framed stream.
- why_it_happens: The parent treats every stdout line as JSON. `console.log` emits plain text onto the same channel, so the next read is not valid JSON.
- accepted_fix: Reserve stdout for protocol frames only. Send diagnostics to stderr or a file logger.
- rejected_fix_patterns:
  - make the parent ignore random parse failures while keeping mixed stdout traffic
  - wrap `json.loads()` in broad retry logic without fixing the stream
  - blame websocket transport when the corruption is already visible on stdout

## Evidence Signals

- strongest_signal: Parent fails on a stdout line that is clearly a human log line, not JSON, and the bridge code logs to stdout right before emitting frames.
- strongest_alternative_explanation: Baileys sometimes emits malformed message IDs.
- why_alternative_is_wrong: The failing line is not a malformed JSON field; it is a plain-text debug line emitted by the bridge.

## Scoring Notes

- full_credit_conditions:
  - identifies stdout as the protocol channel
  - identifies `console.log`/stdout diagnostics as the corruption source
  - moves diagnostics to stderr/file and keeps stdout protocol-only
- partial_credit_conditions:
  - identifies mixed stdout traffic but suggests filtering specific log prefixes instead of separating channels
- fail_conditions:
  - blames Python JSON parser
  - blames websocket packet corruption
  - suggests adding sleeps or reconnects
