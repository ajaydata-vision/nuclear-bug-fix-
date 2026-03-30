# Evaluator

## Metadata

- id: BE-013
- domain: backend
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: nginx, file-upload, body-size, proxy, 413, client_max_body_size

## Ground Truth

- root_cause: Nginx has a default client_max_body_size of 1MB, which is lower than Express's 50MB limit. Nginx rejects the request before it reaches Node.js.
- why_it_happens: Nginx buffers and inspects the request body before proxying it. Its own body size limit is enforced independently of the application's limit. The default is 1MB.
- accepted_fix: Add client_max_body_size 50m; to the Nginx server or location block for the upload endpoint.
- rejected_fix_patterns:
  - increase Express limit further
  - disable Nginx buffering with proxy_request_buffering off

## Evidence Signals

- strongest_signal: Nginx error.log shows body size rejection; direct connection to Node.js succeeds for the same file; 413 is returned before reaching Express
- strongest_alternative_explanation: Multer file size limit too low
- why_alternative_is_wrong: Multer's limit is set to 50MB and direct uploads succeed; the 413 is from Nginx not Multer (Multer would return a different error code and message)

## Scoring Notes

- full_credit_conditions:
  - identifies Nginx client_max_body_size as the bottleneck
  - proposes adding client_max_body_size 50m to Nginx config
  - explains Nginx body inspection before proxying
- partial_credit_conditions:
  - identifies proxy as the issue but does not specify the correct Nginx directive
- fail_conditions:
  - increases Express limit further
  - disables Nginx as a fix
