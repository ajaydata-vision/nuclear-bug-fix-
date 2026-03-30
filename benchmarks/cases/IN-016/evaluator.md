# Evaluator

## Metadata

- id: IN-016
- domain: integration
- track: bohrbug-core
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: grpc, streaming, load-balancer, timeout, keepalive, idle-timeout

## Ground Truth

- root_cause: AWS ALB closes idle TCP connections after 60 seconds (the default idle timeout). Long-running gRPC streams with infrequent messages hit this limit.
- why_it_happens: ALB's idle timeout applies to TCP connections with no data transfer. gRPC uses HTTP/2 which needs keepalive pings to maintain the connection through a load balancer's idle timeout.
- accepted_fix: Configure gRPC keepalive: GRPC_ARG_KEEPALIVE_TIME_MS below the ALB idle timeout (e.g., 30000ms). Or increase ALB idle timeout to 3600s for streaming endpoints.
- rejected_fix_patterns:
  - implement client-side reconnection only without addressing the root cause
  - switch from ALB to NLB without explaining the tradeoff

## Evidence Signals

- strongest_signal: Disconnection occurs at exactly 60 seconds — matching ALB idle timeout; streams with frequent messages unaffected
- strongest_alternative_explanation: gRPC server-side stream timeout
- why_alternative_is_wrong: The disconnection happens at exactly the ALB idle timeout (60s) not the gRPC deadline; the pattern is timing-based not logic-based

## Scoring Notes

- full_credit_conditions:
  - identifies ALB idle timeout as the cause
  - proposes gRPC keepalive configuration below the timeout
  - or increasing ALB idle timeout
- partial_credit_conditions:
  - identifies the 60s pattern but proposes only client reconnection
- fail_conditions:
  - blames gRPC library bug
  - suggests disabling streaming in favour of polling
