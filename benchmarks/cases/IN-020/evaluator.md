# Evaluator

## Metadata

- id: IN-020
- domain: integration
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: content-type, json-parse, microservice, header, axios

## Ground Truth

- root_cause: The upstream service uses res.send() which sends the response as text/html when given a plain string, instead of res.json() which sets the correct Content-Type.
- why_it_happens: Express res.send() with a string argument sets Content-Type to text/html. res.json() automatically sets application/json and serializes the object.
- accepted_fix: Change res.send({ status: 'ok' }) to res.json({ status: 'ok' }), or explicitly set Content-Type: application/json header before sending.
- rejected_fix_patterns:
  - add try/catch in the caller around JSON.parse
  - use text/html content on all microservice endpoints

## Evidence Signals

- strongest_signal: Response body is HTML; Content-Type is text/html not application/json; caller expects JSON
- strongest_alternative_explanation: Error page returned due to uncaught exception
- why_alternative_is_wrong: Status is 200 and the specific handler is reached; the issue is wrong content type from correct handler

## Scoring Notes

- full_credit_conditions:
  - identifies res.send() not setting application/json
  - proposes res.json()
  - explains Content-Type determination by Express
- partial_credit_conditions:
  - identifies content type issue but adds parsing fallback in caller instead of fixing the server
- fail_conditions:
  - adds try/catch in caller without fixing the server
  - suggests switching to XML
