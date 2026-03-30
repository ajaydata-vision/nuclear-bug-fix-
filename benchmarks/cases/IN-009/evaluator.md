# Evaluator

## Metadata

- id: IN-009
- domain: integration
- track: distributed-multi-factor
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: microservices, timeout, circuit-breaker, cascading-failure, go

## Ground Truth

- root_cause: Service A makes blocking downstream calls without explicit timeout or circuit breaking, so slow dependency calls exhaust its workers.
- why_it_happens: Slow responses from Service B tie up Service A resources until upstream traffic collapses too.
- accepted_fix: Add strict client timeouts and a circuit-breaker or fail-fast fallback around Service B calls.
- rejected_fix_patterns:
  - scale Service A only
  - add more CPU without timeouts
  - blame Redis or PostgreSQL without addressing the blocked dependency path

## Evidence Signals

- strongest_signal: Failures propagate from B latency spikes and A threads remain blocked waiting on B
- strongest_alternative_explanation: A itself has a database bottleneck
- why_alternative_is_wrong: The failure can be reproduced by slowing only B while A's local DB path remains healthy

## Scoring Notes

- full_credit_conditions:
  - names downstream timeout/circuit breaker gap
  - proposes explicit timeout plus fail-fast protection
  - verification includes injected latency to B
- partial_credit_conditions:
  - spots missing timeout but omits resource exhaustion mechanism
- fail_conditions:
  - blames queue consumers only
  - recommends scaling without changing dependency behavior
