# Evaluator

## Metadata

- id: BE-016
- domain: backend
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: rate-limit, x-forwarded-for, proxy, ip-address, express-rate-limit

## Ground Truth

- root_cause: req.ip returns the proxy IP (127.0.0.1) instead of the real client IP because app.set('trust proxy') is not configured and X-Forwarded-For is not read.
- why_it_happens: Behind a reverse proxy, all traffic arrives from the proxy's IP. Express's req.ip reflects this unless trust proxy is configured, which causes it to read the real IP from X-Forwarded-For.
- accepted_fix: Add app.set('trust proxy', 1) to trust the first proxy hop, then req.ip will reflect the X-Forwarded-For header value.
- rejected_fix_patterns:
  - use X-Forwarded-For directly without trust proxy setting (vulnerable to spoofing)
  - switch to user ID as rate limit key for authenticated routes only

## Evidence Signals

- strongest_signal: All users rate-limited simultaneously; req.ip logs show the proxy IP not client IPs
- strongest_alternative_explanation: DDoS attack from a single source
- why_alternative_is_wrong: Multiple different users are affected including known legitimate users; it is not a single-source attack

## Scoring Notes

- full_credit_conditions:
  - identifies trust proxy not configured
  - proposes app.set('trust proxy', 1)
  - warns about X-Forwarded-For spoofing if trusting all hops
- partial_credit_conditions:
  - identifies proxy IP issue but reads X-Forwarded-For directly without trust proxy
- fail_conditions:
  - blames rate limit library bug
  - disables rate limiting as the fix
