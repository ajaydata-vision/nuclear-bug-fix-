# Evaluator

## Metadata

- id: JV-004
- domain: java-enterprise
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: jsp, el, expression-language, request-attribute, setAttribute, scriptlet

## Ground Truth

- root_cause: The servlet loads the User object into a local Java variable but never calls req.setAttribute("user", user). JSP Expression Language resolves ${user.name} by searching request/session/application scope attributes — not local Java variables. request.getAttribute("user") returns null because setAttribute was never called.
- why_it_happens: EL ${} resolves names against scope attributes (request, session, application, page) in that order. A local variable in the servlet method is not accessible to the JSP — it only exists on the servlet's call stack. The connection between servlet and JSP is via request attributes set with req.setAttribute().
- accepted_fix: Add req.setAttribute("user", user) in the servlet before the forward. Then ${user.name} will resolve correctly.
- rejected_fix_patterns:
  - use scriptlet to declare User user = ... in JSP (bad practice, does not fix EL)
  - change ${user.name} to ${sessionScope.userId} (wrong — fetches ID not User object)

## Evidence Signals

- strongest_signal: request.getAttribute("user") returns null in scriptlet; System.out confirms user is loaded in servlet; req.setAttribute("user", user) is absent from servlet code
- strongest_alternative_explanation: User class does not have a getName() method accessible to EL (missing getter or wrong naming convention)
- why_alternative_is_wrong: Scriptlet shows request.getAttribute("user") is null — the attribute was never set at all, so the getter convention is irrelevant; if the attribute were set and the getter were wrong, EL would throw a PropertyNotFoundException, not render empty

## Scoring Notes

- full_credit_conditions:
  - identifies missing req.setAttribute("user", user) as root cause
  - explains EL resolves from scope attributes not local variables
  - fix: add req.setAttribute before forward
- partial_credit_conditions:
  - identifies EL issue but suggests changing JSP to use scriptlet as the fix
- fail_conditions:
  - blames EL version incompatibility
  - suggests adding getter method to User class
