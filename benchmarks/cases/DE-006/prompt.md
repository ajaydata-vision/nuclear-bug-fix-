# DE-006: One Instance In The Pool Is Still Old Version

## User Prompt

Our bug appears fixed for most requests, but every so often the old behavior
comes back. Logs from one node show the new sentinel and another node does not.
Why is the fix only working sometimes?

## Context Provided To The Skill

- stack: load-balanced Node.js service with 4 instances
- versions: rolling restart deployment
- environment: staging and production
- logs:
  - three instances report version `2025.04.1`
  - one instance still reports `2025.03.9`
  - requests routed to the old instance show the original bug
- code excerpt:

```txt
lb -> api-1 (new)
lb -> api-2 (new)
lb -> api-3 (new)
lb -> api-4 (old)
```

- reproduction:
  1. Send repeated requests through the load balancer
  2. Observe intermittent old behavior
  3. Correlate failing requests with one older instance
