# Evaluator

## Metadata

- id: JV-005
- domain: java-enterprise
- track: bohrbug-core
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: nio, bytebuffer, clear, compact, channel-write, partial-write

## Ground Truth

- root_cause: buf.clear() is called after to.write(buf) regardless of whether all bytes were written. When to.write(buf) writes only a partial amount (returns fewer bytes than buf.remaining()), the unwritten bytes remain in the buffer. buf.clear() then resets position=0 and limit=capacity, discarding those unwritten bytes. The next read overwrites the now-"empty" buffer, permanently losing the unwritten bytes.
- why_it_happens: clear() unconditionally resets the buffer to an empty state. compact() copies unread/unsent bytes to the start of the buffer and positions after them, preserving them for the next write attempt. Under load, socket send buffers fill up causing partial writes — this is normal NIO behavior that compact() handles correctly.
- accepted_fix: Replace buf.clear() with buf.compact(). compact() preserves any bytes not yet written and positions the buffer correctly for the next read. Also add a write loop or OP_WRITE registration for full correctness.
- rejected_fix_patterns:
  - increase buffer size (reduces frequency but does not fix the data loss)
  - switch to blocking channels (changes concurrency model, not the clear/compact issue)

## Evidence Signals

- strongest_signal: Logs show "Sent 847 bytes" when 1024 were read (partial write); buf.clear() called immediately after; "Read next chunk" overwrites buffer
- strongest_alternative_explanation: from.read() returning partial data (incomplete message read)
- why_alternative_is_wrong: The log shows "Read 1024 bytes" (full read); the partial write is on the send side (847 bytes sent); the clear() after partial send is where data is lost

## Scoring Notes

- full_credit_conditions:
  - identifies buf.clear() after partial write as root cause
  - explains difference between clear() and compact()
  - proposes buf.compact() as fix
- partial_credit_conditions:
  - identifies partial write issue but suggests write loop without fixing clear/compact
- fail_conditions:
  - blames network packet loss
  - suggests increasing TCP buffer sizes at OS level
