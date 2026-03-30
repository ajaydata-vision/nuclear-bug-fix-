# Evaluator

## Metadata

- id: FE-006
- domain: frontend
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: react, form, event, submit, onclick-vs-onsubmit

## Ground Truth

- root_cause: The submit handler is bound to onClick on the button rather than onSubmit on the form, and e.preventDefault() is never called, so the default form submission fires.
- why_it_happens: HTML forms submit on button click by default. Without e.preventDefault(), the browser performs a full-page GET/POST. The handler receives the MouseEvent not the form data.
- accepted_fix: Move handler to form's onSubmit and call e.preventDefault(): <form onSubmit={e => { e.preventDefault(); handleSubmit(formData) }}>
- rejected_fix_patterns:
  - change button type to button to suppress submit without explaining the real pattern
  - use ajax without explaining preventDefault

## Evidence Signals

- strongest_signal: Page reloads on submit and no console output appears
- strongest_alternative_explanation: JavaScript error silently preventing execution
- why_alternative_is_wrong: A JS error would appear in the console; page reload confirms default browser form submission

## Scoring Notes

- full_credit_conditions:
  - identifies missing e.preventDefault()
  - proposes onSubmit on form element
  - explains default browser form submission
- partial_credit_conditions:
  - adds type=button to suppress reload but does not wire up onSubmit correctly
- fail_conditions:
  - suggests using fetch directly without fixing the event binding
