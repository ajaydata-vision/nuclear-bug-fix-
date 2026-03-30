# Evaluator

## Metadata

- id: DE-005
- domain: general
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: tls, ssl, certificate, expiry, https, certificate-error

## Ground Truth

- root_cause: The TLS certificate for the API endpoint expired at midnight and was not renewed, causing all HTTPS clients to reject the connection.
- why_it_happens: TLS certificates have a validity period. When a certificate expires, clients that verify TLS (the default) will refuse to connect. The fix requires renewing the certificate on the server.
- accepted_fix: Renew the TLS certificate on the API server. Use certificate monitoring and automatic renewal (Let's Encrypt with certbot auto-renew, or ACM with auto-renewal enabled) to prevent recurrence.
- rejected_fix_patterns:
  - add rejectUnauthorized: false to bypass TLS verification
  - update the API URL to HTTP

## Evidence Signals

- strongest_signal: Error started exactly at midnight; CERT_HAS_EXPIRED error code; curl -v shows expired NotAfter date
- strongest_alternative_explanation: API server outage
- why_alternative_is_wrong: The server is responding; the TLS handshake fails before any HTTP request is made, which is a certificate problem

## Scoring Notes

- full_credit_conditions:
  - identifies expired TLS certificate
  - proposes renewing the certificate
  - recommends auto-renewal to prevent recurrence
- partial_credit_conditions:
  - identifies SSL error but proposes disabling TLS verification as the fix
- fail_conditions:
  - suggests rejectUnauthorized: false as the fix
  - blames the API provider without identifying the cert expiry
