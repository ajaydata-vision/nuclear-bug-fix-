# Evaluator

## Metadata

- id: BE-002
- domain: backend
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: express, route-order, catch-all, 404, middleware

## Ground Truth

- root_cause: The catch-all 404 handler is mounted before the route definition, so every request matches the catch-all before reaching the intended route.
- why_it_happens: Express matches routes in registration order. A catch-all (app.use with no path) matches every request. Placing it before routes means it intercepts all traffic.
- accepted_fix: Move the catch-all 404 handler to after all route definitions.
- rejected_fix_patterns:
  - add a specific exclusion in the catch-all for known routes
  - wrap the catch-all in a condition

## Evidence Signals

- strongest_signal: The route is defined but never reached; adding a log to it confirms it is never called
- strongest_alternative_explanation: Route path typo
- why_alternative_is_wrong: The path is correct; the issue is ordering — placing a log in the catch-all confirms it runs first

## Scoring Notes

- full_credit_conditions:
  - identifies catch-all before route as the cause
  - proposes moving catch-all to end
  - explains Express registration order
- partial_credit_conditions:
  - spots routing issue but suggests adding the route before the catch-all without explaining why
- fail_conditions:
  - blames Express bug
  - adds duplicate route definition
