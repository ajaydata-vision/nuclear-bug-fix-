# Evaluator

## Metadata

- id: RC-010
- domain: backend
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: file-write, concurrent, interleaving, log-corruption, mutex

## Ground Truth

- root_cause: Concurrent file writes from multiple processes interleave at the OS level. A write of N bytes is not atomic; another process's write can occur between bytes.
- why_it_happens: Python's file append mode is not process-safe. The OS may schedule another process's write between the buffer flush operations of the first write.
- accepted_fix: Use a logging queue where a single writer process consumes from it, or use Python's logging module with a SocketHandler, or use file-level locks (fcntl.flock) around each write.
- rejected_fix_patterns:
  - use threading.Lock() — only protects within a single process not across processes
  - reduce to a single worker process

## Evidence Signals

- strongest_signal: Corruption correlates exactly with multi-process execution; single process produces correct output; half-entries in log confirm interleaved writes
- strongest_alternative_explanation: JSON serialization bug in event data
- why_alternative_is_wrong: JSON entries are syntactically correct when written by a single process; corruption is always at the boundary between two entries from different processes

## Scoring Notes

- full_credit_conditions:
  - identifies non-atomic file write under multiprocessing
  - proposes single writer process with queue or fcntl.flock
  - explains thread-safety vs process-safety distinction
- partial_credit_conditions:
  - adds threading.Lock without realising it does not work across processes
- fail_conditions:
  - switches to JSON Lines format without addressing concurrency
  - uses try/except to discard corrupt entries
