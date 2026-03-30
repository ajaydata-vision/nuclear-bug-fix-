# Evaluator

## Metadata

- id: VE-006
- domain: version-external-intelligence
- track: regression-version
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: oauth, rfc6749, token-endpoint, protocol, pkce

## Ground Truth

- root_cause: The client violates OAuth 2.0 token endpoint requirements by using `GET` instead of a form-encoded `POST`.
- why_it_happens: Authorization code exchange must be sent to the token endpoint as a POST request with the proper encoding.
- accepted_fix: Change the token exchange to `POST` with `application/x-www-form-urlencoded` body per OAuth 2.0.
- rejected_fix_patterns:
  - rotate the client secret
  - blame provider outage
  - retry the same GET request

## Evidence Signals

- strongest_signal: The provider returns method rejection exactly at the token exchange step
- strongest_alternative_explanation: The authorization code is expired
- why_alternative_is_wrong: Expired code would not explain a method-level 405 on the endpoint contract

## Scoring Notes

- full_credit_conditions:
  - cites protocol or docs mismatch
  - changes request to POST form-encoded body
  - verification includes successful code exchange
- partial_credit_conditions:
  - spots token request construction issue but misses RFC grounding
- fail_conditions:
  - changes only headers while keeping GET
  - blames redirect URI mismatch as the main cause of 405
