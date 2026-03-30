# Evaluator

## Metadata

- id: IN-019
- domain: integration
- track: distributed-multi-factor
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: rate-limit, third-party-api, 429, backoff, cascading-failure, circuit-breaker

## Ground Truth

- root_cause: Immediate retry on 429 creates a retry storm that amplifies load on the rate-limited API, making recovery impossible.
- why_it_happens: On 429, every caller immediately retries. N callers × immediate retry = N times the original load. The API cannot recover because retries prevent the rate window from clearing.
- accepted_fix: Implement exponential backoff with jitter on 429: wait Retry-After header value or exponential delay before retrying. Add a circuit breaker to shed load when 429 rate is high.
- rejected_fix_patterns:
  - increase rate limit quota as the only fix
  - disable retries entirely

## Evidence Signals

- strongest_signal: 429 followed by immediate retry loop; API cannot recover while retries continue
- strongest_alternative_explanation: Payment API outage unrelated to rate limiting
- why_alternative_is_wrong: The specific 429 response code indicates rate limiting not an outage; recovery is possible with backoff

## Scoring Notes

- full_credit_conditions:
  - identifies immediate retry amplifying rate limit violation
  - proposes exponential backoff with jitter and Retry-After
  - recommends circuit breaker for systemic protection
- partial_credit_conditions:
  - adds backoff without jitter (may still synchronize retries)
- fail_conditions:
  - increases rate limit quota without fixing client retry behavior
  - disables retries entirely
