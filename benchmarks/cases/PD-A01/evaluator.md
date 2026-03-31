# Evaluator

## Metadata

- id: PD-A01
- domain: python-desktop
- track: bohrbug-core
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyqt6, qasync, asyncio, event-loop, startup, desktop

## Ground Truth

- root_cause: Startup creates tasks on a plain asyncio loop that is different from the qasync Qt loop actually being run. `bootstrap()` is queued on the wrong loop, so it never advances.
- why_it_happens: qasync only drives the loop that wraps the Qt app. `asyncio.set_event_loop(asyncio.new_event_loop())` creates a second loop and makes it current before `create_task()` is called. The task is attached to that plain loop, while `qt_loop.run_forever()` pumps a different loop.
- accepted_fix: Set the current event loop to the `qasync.QEventLoop(app)` before scheduling any tasks, and ensure all startup tasks are created on that same loop.
- rejected_fix_patterns:
  - add sleeps or timers around `restore_session()`
  - retry HTTP auth without fixing loop ownership
  - create an extra background loop for startup tasks

## Evidence Signals

- strongest_signal: Log shows a bootstrap task created on one loop ID while the app is run by `qt_loop`, and startup tasks never progress despite the UI showing.
- strongest_alternative_explanation: `restore_session()` awaits a network call that never returns.
- why_alternative_is_wrong: A stuck network call would still require the coroutine to start; the absence of any later coroutine-body log combined with split loop creation points to scheduling on an unpumped loop.

## Scoring Notes

- full_credit_conditions:
  - identifies that two different event loops are being created/used
  - explains that the startup task is scheduled on the wrong loop
  - fixes by making qasync's loop the active loop before any task creation
- partial_credit_conditions:
  - says qasync setup is wrong but does not explain that the task is bound to the wrong loop
  - suggests `qasync.run()` without identifying the exact split-loop mechanism
- fail_conditions:
  - blames `httpx` timeout
  - blames missing `await` inside `restore_session()`
  - suggests adding `asyncio.sleep()` to let startup finish
