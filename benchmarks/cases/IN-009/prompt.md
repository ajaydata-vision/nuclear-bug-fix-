# IN-009: Cascading Failure Because Downstream Calls Never Time Out

## User Prompt

When Service B becomes slow, Service A starts timing out, then queue consumers
back up, and eventually the whole request path looks broken. The bug appears to
be everywhere at once. What is the real root cause?

## Context Provided To The Skill

- stack: Go 1.22 + HTTP microservices + PostgreSQL + Redis
- versions: Kubernetes deployment
- environment: production under traffic bursts
- logs:
  - Service B latency spikes from 80ms to 12s
  - Service A worker count remains fully busy waiting on B
  - upstream requests to A return 504
- code excerpt:

```go
resp, err := http.Get(serviceBURL + "/quote?id=" + id)
if err != nil {
    return err
}
defer resp.Body.Close()
```

- reproduction:
  1. Add 12s latency to Service B
  2. Send normal traffic to Service A
  3. Observe cascading slowdown and failures
