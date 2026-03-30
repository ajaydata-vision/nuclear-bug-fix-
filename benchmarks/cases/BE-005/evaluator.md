# Evaluator

## Metadata

- id: BE-005
- domain: backend
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: auth, bearer-token, authorization-header, jwt, malformed

## Ground Truth

- root_cause: The Authorization header is sent as 'BearerTOKEN' without a space, which is not a valid Bearer token format.
- why_it_happens: String concatenation 'Bearer' + token omits the required space between the scheme and the token. The server's Authorization header parser expects 'Bearer TOKEN'.
- accepted_fix: Add a space: 'Bearer ' + token or use a template literal: `Bearer ${token}`
- rejected_fix_patterns:
  - use lowercase 'bearer'
  - switch to a different auth scheme

## Evidence Signals

- strongest_signal: Postman works with same token; network tab shows missing space in Authorization header
- strongest_alternative_explanation: Token encoding difference between app and Postman
- why_alternative_is_wrong: The token value is identical; only the prefix differs as visible in the network tab

## Scoring Notes

- full_credit_conditions:
  - identifies missing space in 'Bearer' prefix
  - proposes 'Bearer ' + token or template literal
  - confirms by inspecting network tab
- partial_credit_conditions:
  - identifies header format issue but does not pinpoint the space
- fail_conditions:
  - blames backend auth logic
  - suggests using a different token type
