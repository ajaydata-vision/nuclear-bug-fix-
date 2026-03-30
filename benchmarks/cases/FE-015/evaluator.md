# Evaluator

## Metadata

- id: FE-015
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: cors, credentials, preflight, access-control, cookies

## Ground Truth

- root_cause: The CORS spec prohibits wildcard Access-Control-Allow-Origin when credentials: include is used. The backend must reflect the exact requesting origin.
- why_it_happens: Cookies and credentials cannot be sent to a wildcard origin for security reasons. The server must echo the specific origin and set Access-Control-Allow-Credentials: true.
- accepted_fix: Configure CORS to reflect the specific origin: cors({ origin: req.headers.origin, credentials: true }) and verify Access-Control-Allow-Credentials: true is sent.
- rejected_fix_patterns:
  - remove credentials from fetch without explaining the auth impact
  - use CORS proxy

## Evidence Signals

- strongest_signal: Browser error message explicitly states the wildcard/credentials incompatibility
- strongest_alternative_explanation: Missing Access-Control-Allow-Methods header
- why_alternative_is_wrong: The error message specifically cites Access-Control-Allow-Origin wildcard; methods issue would produce a different error

## Scoring Notes

- full_credit_conditions:
  - identifies wildcard origin incompatible with credentials
  - proposes reflecting specific origin
  - mentions Access-Control-Allow-Credentials: true
- partial_credit_conditions:
  - identifies CORS issue but proposes removing credentials mode
- fail_conditions:
  - suggests disabling CORS entirely
  - blames browser security policy as unfixable
