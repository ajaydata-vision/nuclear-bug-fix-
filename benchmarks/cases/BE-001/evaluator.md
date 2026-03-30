# Evaluator

## Metadata

- id: BE-001
- domain: backend
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: express, body-parser, middleware-order, req-body

## Ground Truth

- root_cause: express.json() middleware is registered after the route, so it never runs before the handler processes the request.
- why_it_happens: Express processes middleware and routes in the order they are registered. A middleware registered after a route does not run for that route.
- accepted_fix: Move app.use(express.json()) before all route definitions.
- rejected_fix_patterns:
  - add body-parser as a separate dependency
  - parse body manually in each handler

## Evidence Signals

- strongest_signal: req.body undefined despite correct Content-Type; middleware declared after route in source
- strongest_alternative_explanation: Wrong Content-Type header sent by client
- why_alternative_is_wrong: Content-Type is confirmed correct; moving middleware before route fixes the issue

## Scoring Notes

- full_credit_conditions:
  - identifies middleware registered after route
  - proposes moving express.json() before routes
  - explains Express middleware order
- partial_credit_conditions:
  - identifies body parsing issue but suggests adding body-parser package
- fail_conditions:
  - blames Express bug
  - suggests parsing body with raw streams in handler
