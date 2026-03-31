# Evaluator

## Metadata

- id: PD-001
- domain: python-desktop
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyqt6, qasync, async-slot, coroutine, signal-slot

## Ground Truth

- root_cause: The Qt signal is connected directly to an `async def`, so Qt calls the function synchronously and receives a coroutine object that nobody awaits or schedules.
- why_it_happens: Qt signal/slot connections expect a normal callable. Without `@asyncSlot()` or explicit task scheduling, the coroutine body never runs.
- accepted_fix: Use `@qasync.asyncSlot()` on the slot or connect the signal to a synchronous wrapper that schedules `send_reply()` on the running qasync loop.
- rejected_fix_patterns:
  - add more awaits inside `send_reply`
  - wrap the body in try/except without fixing signal connection
  - suppress the warning and keep the same slot wiring

## Evidence Signals

- strongest_signal: Click signal fires, but the slot body never logs and shutdown shows `coroutine was never awaited`.
- strongest_alternative_explanation: `mailer.send_current_draft()` hangs.
- why_alternative_is_wrong: A hanging mailer call would still log `Sending...` from inside the coroutine. Here the coroutine body is never entered.

## Scoring Notes

- full_credit_conditions:
  - identifies that a raw coroutine is connected to a Qt signal
  - explains why Qt does not await the coroutine automatically
  - fixes with `@asyncSlot()` or explicit task scheduling
- partial_credit_conditions:
  - identifies async-slot wiring as the problem but does not explain the coroutine object behavior
- fail_conditions:
  - blames SMTP server latency
  - suggests adding retries to the mailer
  - rewrites the feature into threads without addressing the slot contract
