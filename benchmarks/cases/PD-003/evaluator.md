# Evaluator

## Metadata

- id: PD-003
- domain: python-desktop
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyqt6, thread-affinity, widget, background-thread, qobject

## Ground Truth

- root_cause: The worker thread calls `status_label.setText()` and `results_table.setRowCount()` directly, mutating Qt widgets from a non-GUI thread.
- why_it_happens: Qt widgets and most QObjects must be accessed from their owning thread, typically the main GUI thread. Direct cross-thread mutation violates thread-affinity rules.
- accepted_fix: Return results to the GUI thread via a signal, queued connection, or main-thread callback, and perform all widget updates there.
- rejected_fix_patterns:
  - add locks around widget access
  - retry the widget update from the same worker thread
  - move more UI code into the worker thread

## Evidence Signals

- strongest_signal: Qt thread-affinity error appears immediately after worker completion, and the worker code directly touches widgets.
- strongest_alternative_explanation: Backend search returns malformed rows that crash the table model.
- why_alternative_is_wrong: Malformed rows would affect table content, not produce a thread-affinity error tied to worker completion.

## Scoring Notes

- full_credit_conditions:
  - identifies direct widget mutation from a background thread
  - explains Qt thread-affinity requirements
  - fixes by marshaling updates back to the GUI thread
- partial_credit_conditions:
  - identifies a threading problem but suggests generic locking without preserving GUI-thread ownership
- fail_conditions:
  - blames backend search data
  - blames garbage collection
  - suggests increasing thread count
