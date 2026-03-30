# Evaluator

## Metadata

- id: BE-006
- domain: backend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: cookie, sameSite, domain, session, cross-origin, auth

## Ground Truth

- root_cause: SameSite=Strict prevents the cookie from being sent on cross-site requests from app.example.com to api.example.com, even though they share a base domain.
- why_it_happens: SameSite=Strict blocks cookies on all cross-site requests including subdomains by strict interpretation. The correct setting for subdomain cross-site is SameSite=Lax or None with Secure for cross-origin.
- accepted_fix: Set SameSite: 'lax' and domain: '.example.com' (with leading dot to cover all subdomains), or use SameSite: 'none' with secure: true for fully cross-origin setups.
- rejected_fix_patterns:
  - disable cookie-based auth and use localStorage tokens
  - set SameSite=None without Secure

## Evidence Signals

- strongest_signal: Cookie is set after login but browser's network tab shows it absent from subsequent requests
- strongest_alternative_explanation: Session store losing data between requests
- why_alternative_is_wrong: The cookie is never sent to begin with; the session store is never consulted because the cookie is absent

## Scoring Notes

- full_credit_conditions:
  - identifies SameSite=Strict blocking cross-subdomain requests
  - proposes Lax or None+Secure with correct domain
  - explains SameSite semantics
- partial_credit_conditions:
  - identifies cookie not being sent but proposes switching to token auth without explaining the root cause
- fail_conditions:
  - blames browser bug
  - suggests clearing browser cache
