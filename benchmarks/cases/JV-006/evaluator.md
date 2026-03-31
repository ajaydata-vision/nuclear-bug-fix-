# Evaluator

## Metadata

- id: JV-006
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: nio, channel-write, partial-write, non-blocking, bytebuffer, socket

## Ground Truth

- root_cause: SocketChannel.write() in non-blocking mode does not guarantee writing all bytes. It returns the number of bytes actually written, which can be less than buffer.remaining() when the socket send buffer is full. The code calls write() once and proceeds regardless, silently losing the remaining bytes.
- why_it_happens: Non-blocking I/O by definition does not block when the socket buffer is full — it writes what fits and returns. The caller is responsible for detecting a partial write (returned value < buffer.remaining()) and retrying. This is fundamental NIO contract: write() returns bytes written, never throws for a partial write.
- accepted_fix: Wrap write() in a while loop checking buffer.hasRemaining(). For non-blocking channels where write returns 0 (socket buffer completely full), register OP_WRITE on the selector and continue when the socket becomes writable again.
- rejected_fix_patterns:
  - switch channel to blocking mode (changes entire server architecture)
  - increase socket send buffer size at OS level (reduces frequency, does not fix the logic)
  - check written == responseBytes.length (correct check but fix must be the write loop)

## Evidence Signals

- strongest_signal: Log shows "Write call returned: 65536" for 98304-byte payload (65536 < 98304 = partial write); "Response sent successfully" logged immediately after single write call
- strongest_alternative_explanation: Client-side TCP buffer full causing receiver to close connection prematurely
- why_alternative_is_wrong: Client never closes the connection — it receives truncated data and tries to parse it. The truncation happens on the server send side as evidenced by the 65536 return value.

## Scoring Notes

- full_credit_conditions:
  - identifies single write() call not handling partial write
  - explains non-blocking channel write() semantics (returns bytes written, may be < remaining)
  - proposes while(buf.hasRemaining()) write loop
- partial_credit_conditions:
  - identifies partial write but only adds a check without the retry loop
- fail_conditions:
  - blames network MTU or TCP fragmentation
  - suggests using blocking mode without explaining the root cause
