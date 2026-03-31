# Evaluator

## Metadata

- id: PD-004
- domain: python-desktop
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyqt6, qasync, shutdown, scheduler, websocket, cleanup

## Ground Truth

- root_cause: The shutdown path accepts the close event before long-lived websocket
  and scheduler work has actually stopped, so pending async tasks and background
  activity keep the process alive.
- why_it_happens: Qt closing the window is not the same as cleaning up the event
  loop. If background tasks are not cancelled/awaited before exit, they keep the
  Python process alive or leave pending-task warnings.
- accepted_fix: Stop the scheduler, close the websocket, cancel and await long-lived
  tasks, and only then allow the app to exit.
- rejected_fix_patterns:
  - call `os._exit(0)` as the primary fix
  - ignore pending-task warnings
  - make the UI close faster without cleaning up the background work

## Evidence Signals

- strongest_signal: The close path logs cleanup requests but still shows pending
  tasks alive after the window is closed.
- strongest_alternative_explanation: The OS is keeping the process alive due to
  a stray GUI window.
- why_alternative_is_wrong: The GUI window is already gone; the logs show the
  websocket and scheduler tasks are what remain alive.

## Scoring Notes

- full_credit_conditions:
  - identifies incomplete shutdown/cleanup as the root cause
  - explains why background tasks outlive the closed window
  - fixes by ordering shutdown and awaiting cancellation
- partial_credit_conditions:
  - identifies cleanup as the problem but only suggests forcing exit
- fail_conditions:
  - blames Qt painting or window manager behavior
  - suggests sleep/retry loops during shutdown
  - ignores pending tasks and just suppresses warnings
