# Evaluator

## Metadata

- id: IN-014
- domain: integration
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kubernetes, health-check, grpc, http, probe, service-mesh, istio

## Ground Truth

- root_cause: The livenessProbe uses httpGet against a gRPC port. gRPC uses HTTP/2 framing which is not compatible with a plain HTTP/1.1 GET probe.
- why_it_happens: Kubernetes httpGet probes send HTTP/1.1 requests. gRPC endpoints speak HTTP/2 with binary framing. The probe receives a protocol error and reports the pod as unhealthy.
- accepted_fix: Switch the probe to use grpc type (Kubernetes 1.24+): livenessProbe: grpc: { port: 50051 }. Or add a separate HTTP health endpoint alongside gRPC, or use a tcpSocket probe as a minimal connectivity check.
- rejected_fix_patterns:
  - expose gRPC service on HTTP/1.1 to satisfy the probe
  - disable the liveness probe entirely

## Evidence Signals

- strongest_signal: HTTP probe connection refused on the gRPC port; service responds correctly to gRPC clients; probe type mismatch is the only difference
- strongest_alternative_explanation: gRPC service not starting correctly
- why_alternative_is_wrong: gRPC clients can connect successfully to the same port; the issue is the HTTP probe protocol mismatch not the service itself

## Scoring Notes

- full_credit_conditions:
  - identifies HTTP probe against gRPC port as protocol mismatch
  - proposes grpc probe type or separate HTTP health endpoint
  - explains HTTP/1.1 vs HTTP/2 incompatibility
- partial_credit_conditions:
  - identifies probe failure but proposes only tcpSocket without explaining the protocol issue
- fail_conditions:
  - disables liveness probe
  - exposes gRPC service on additional HTTP/1.1 port as permanent architecture change
