# Evaluator

## Metadata

- id: FE-019
- domain: frontend
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: service-worker, cache, deploy, stale-assets, pwa

## Ground Truth

- root_cause: The service worker cache strategy keeps serving an older asset set after deploy.
- why_it_happens: Cached JS is returned before the network, and the worker update / cache versioning flow does not invalidate old assets promptly.
- accepted_fix: Version caches and update the service worker lifecycle correctly, or invalidate stale assets so old bundles cannot keep winning.
- rejected_fix_patterns:
  - blame the API
  - blame React state
  - tell users to hard refresh as the fix

## Evidence Signals

- strongest_signal: Old hashed JS continues to be served from client cache while HTML and release output are already updated
- strongest_alternative_explanation: CDN edge node is stale
- why_alternative_is_wrong: Hard refresh fixes the issue client-side and the stale file is specifically coming from the service worker cache

## Scoring Notes

- full_credit_conditions:
  - identifies stale service worker cache as primary cause
  - proposes cache versioning, worker update, or stale asset invalidation
  - verification includes deploy and revisit flow without hard refresh
- partial_credit_conditions:
  - identifies stale client cache but not the worker lifecycle issue
- fail_conditions:
  - blames backend deploy
  - suggests only clearing browser cache manually
