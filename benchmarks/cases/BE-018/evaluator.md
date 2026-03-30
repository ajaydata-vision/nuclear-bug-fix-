# Evaluator

## Metadata

- id: BE-018
- domain: backend
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: firewall, outbound, network, external-api, production-only

## Ground Truth

- root_cause: Production VPC security groups block outbound HTTPS (port 443) to external hosts. The code is correct but infrastructure restricts the traffic.
- why_it_happens: Cloud environments often have restrictive default outbound rules for security. External API calls require explicit outbound rules in security groups or firewall policies.
- accepted_fix: Add an outbound security group rule allowing HTTPS (TCP 443) to the third-party API's IP range or domain, or route through a NAT gateway with appropriate rules.
- rejected_fix_patterns:
  - proxy the request through a Lambda function to bypass the firewall
  - change the API call to HTTP instead of HTTPS

## Evidence Signals

- strongest_signal: ETIMEDOUT only in production; internal calls work; curl from production server also times out
- strongest_alternative_explanation: Third-party API outage
- why_alternative_is_wrong: Dev environment successfully calls the same API; the issue is specific to the production network path

## Scoring Notes

- full_credit_conditions:
  - identifies outbound firewall blocking the connection
  - proposes security group rule update
  - confirms by testing curl from production server
- partial_credit_conditions:
  - identifies network issue but proposes proxying as permanent solution without fixing root cause
- fail_conditions:
  - blames third-party API
  - suggests retry logic as the fix
