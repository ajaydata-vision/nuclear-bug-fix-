# Evaluator

## Metadata

- id: FE-021
- domain: frontend
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: fetch, http, 4xx, error-handling, response-ok, javascript, async

## Ground Truth

- root_cause: `fetch()` only rejects its promise on network-level failures (DNS failure, connection refused, timeout). HTTP error status codes (4xx, 5xx) resolve the promise successfully — `response.ok` is `false` but no exception is thrown. The `catch` block never executes for a 400 response, so the error body is parsed as if it were a success body, `data.user` is `undefined`, and execution continues to `navigate('/dashboard')`.
- why_it_happens: The Fetch API specification requires the promise to resolve for any complete HTTP response regardless of status code. Only a failure to complete the HTTP request at the network level rejects the promise. This is by design — it separates transport errors from application errors. Code that uses `try/catch` alone without checking `response.ok` silently swallows all HTTP application errors.
- accepted_fix: Check `response.ok` after `fetch()` and throw explicitly for non-OK responses before parsing the body. Also guard `navigate('/dashboard')` against undefined user.
- rejected_fix_patterns:
  - add a second catch block
  - increase the fetch timeout
  - check for `data.error` in the response body as the primary error detection mechanism (fragile — does not generalize to all error responses)

## Evidence Signals

- strongest_signal: Network tab shows 400; catch block never executes (no `[AUTH] login failed` log); `fetch()` used without `response.ok` check
- strongest_alternative_explanation: The server is returning 200 with an error body and the status code in the network tab is being misread
- why_alternative_is_wrong: The prompt explicitly shows the network tab result as 400 and the response body as `{"error":"Invalid credentials"}`. A 200 with error body would execute the catch only if the body parsing threw — `response.json()` does not throw for valid JSON regardless of content. The symptom (catch never runs for a 400) uniquely identifies the missing response.ok check.

## Scoring Notes

- full_credit_conditions:
  - identifies fetch() not throwing on 4xx as root cause
  - prescribes response.ok check before body parsing
  - provides corrected code with throw on non-ok response
- partial_credit_conditions:
  - identifies the issue but prescribes checking `data.error` in the body instead of `response.ok` (works for this specific API but is not the correct general fix — body-based checks don't generalise to APIs with different error shapes)
  - diagnoses fetch() silent 4xx correctly but also incorrectly adds a second catch block as a fix
- fail_conditions:
  - recommends adding a second catch block
  - suggests the server should return a different status code
  - blames the navigate() call without identifying why user is undefined
