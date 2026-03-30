# IN-014: Service Mesh Health Check Fails Because Wrong Protocol Configured

## User Prompt

Our gRPC service keeps getting killed by Kubernetes even though it is running correctly. The health check always fails. What is configured wrong?

## Context Provided To The Skill

- stack: Node.js 20.11, gRPC, Kubernetes 1.29, Istio 1.20
- environment: production Kubernetes cluster with Istio service mesh
- logs:
- pod repeatedly marked Unhealthy and restarted
  - livenessProbe is HTTP GET /healthz
  - service exposes only gRPC (no HTTP health endpoint)
  - probe returns connection refused
  - gRPC health check protocol (grpc.health.v1) is implemented on the service
- code excerpt:
```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 50051       # gRPC port — not HTTP
  initialDelaySeconds: 10
  periodSeconds: 5
```
- reproduction:
1. Deploy gRPC service to Kubernetes
2. Pod starts successfully
3. livenessProbe fails (HTTP GET against gRPC port)
4. Pod restarted repeatedly — CrashLoopBackOff
