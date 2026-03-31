# Evaluator

## Metadata

- id: PD-002
- domain: python-desktop
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyqt6, qasync, blocking-io, imaplib, ui-freeze

## Ground Truth

- root_cause: Synchronous `imaplib` network I/O is executed directly on the UI/qasync event loop thread, blocking repaint and event processing.
- why_it_happens: qasync integrates Qt and asyncio but does not make synchronous libraries non-blocking. `IMAP4_SSL`, `login`, and `search` block the main thread.
- accepted_fix: Move the blocking IMAP work off the UI loop using `asyncio.to_thread()` or an executor/worker, then marshal results back to the main thread.
- rejected_fix_patterns:
  - add `await asyncio.sleep(0)` around `imaplib` calls
  - increase Qt timer intervals
  - blame repaint performance instead of blocking I/O

## Evidence Signals

- strongest_signal: UI freeze duration matches the synchronous IMAP call duration and both logs occur on `MainThread`.
- strongest_alternative_explanation: Server latency alone is making the sync feel slow.
- why_alternative_is_wrong: Slow server response explains duration, not a frozen UI. The UI freezing proves blocking work is on the event loop thread.

## Scoring Notes

- full_credit_conditions:
  - identifies blocking `imaplib` calls on the main loop as the cause
  - explains that qasync does not make sync libraries async
  - moves blocking work to `to_thread()`/executor/worker
- partial_credit_conditions:
  - identifies blocking I/O but suggests replacing the whole IMAP stack without an immediate fix
- fail_conditions:
  - blames Qt painting
  - suggests adding retries to IMAP
  - recommends more sleeps/yields around the same blocking code
