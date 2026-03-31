# Evaluator

## Metadata

- id: JV-A03
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: nio, bytebuffer, flip, channel, write, java-nio

## Ground Truth

- root_cause: ByteBuffer.flip() is not called before channel.write(). After buffer.put(data), position=48291 and limit=48291 (capacity). channel.write(buffer) reads from position to limit — an empty range of 0 bytes. flip() would set limit=48291, position=0, making all 48291 bytes available for writing.
- why_it_happens: ByteBuffer has two modes — filling (writing into the buffer) and draining (reading from the buffer / sending via channel). After put(), the buffer is in filling mode with position at end. flip() switches to draining mode by setting limit=current position, position=0. Without flip(), write() sees no bytes remaining (position==limit) and writes nothing.
- accepted_fix: Call buffer.flip() immediately before client.write(buffer).
- rejected_fix_patterns:
  - use buffer.rewind() instead (rewind sets position=0 but does not change limit — sends capacity bytes of garbage after the data)
  - allocate a new buffer from data directly using ByteBuffer.wrap(data) (valid workaround, but does not fix the underlying flip() understanding)

## Evidence Signals

- strongest_signal: Write returns 0 bytes despite buffer being populated; no exception; file read confirmed at 48291 bytes; buffer.put(data) called but buffer.flip() absent before write
- strongest_alternative_explanation: SocketChannel is in blocking mode and the client is not reading fast enough, causing write to return 0
- why_alternative_is_wrong: A blocking-mode SocketChannel.write() blocks until at least one byte is written or an error occurs — it does not return 0. The 0-byte write is only possible when buffer.remaining() == 0, which is the flip() absence symptom.

## Scoring Notes

- full_credit_conditions:
  - identifies missing buffer.flip() as the root cause
  - explains ByteBuffer position/limit state before and after flip()
  - provides the one-line fix: buffer.flip() before client.write(buffer)
- partial_credit_conditions:
  - suggests ByteBuffer.wrap(data) as an alternative without explaining flip()
  - identifies the write returning 0 as the symptom but does not name flip()
- fail_conditions:
  - blames SocketChannel blocking mode
  - suggests increasing buffer capacity
  - recommends switching to FileChannel.transferTo()
