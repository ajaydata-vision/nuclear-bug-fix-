# Evaluator

## Metadata

- id: IN-010
- domain: integration
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: api-gateway, header-stripping, authorization, nginx, proxy

## Ground Truth

- root_cause: The API Gateway integration is not configured to pass the Authorization header to the backend. It strips it by default.
- why_it_happens: AWS API Gateway does not forward all headers automatically. Headers must be explicitly mapped in the integration request parameters or the API must use HTTP proxy integration which passes all headers.
- accepted_fix: Configure API Gateway to forward the Authorization header: add RequestParameters mapping for method.request.header.Authorization, or switch to HTTP_PROXY integration type.
- rejected_fix_patterns:
  - move auth to query parameter instead of header
  - disable authentication as a temporary fix

## Evidence Signals

- strongest_signal: Authorization header present in client request but absent in Lambda log; works without the gateway
- strongest_alternative_explanation: Lambda function role lacking permissions
- why_alternative_is_wrong: Lambda permissions affect what Lambda can do in AWS; the 401 is the Lambda itself rejecting the request due to missing auth header

## Scoring Notes

- full_credit_conditions:
  - identifies API Gateway not forwarding Authorization header
  - proposes header mapping or HTTP_PROXY integration
  - confirms by checking API Gateway access logs
- partial_credit_conditions:
  - identifies gateway as the issue but does not specify the header mapping fix
- fail_conditions:
  - moves auth logic to a Lambda authorizer without understanding the header stripping
  - blames client for not sending the header
