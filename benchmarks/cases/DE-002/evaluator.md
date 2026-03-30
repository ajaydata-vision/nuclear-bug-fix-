# Evaluator

## Metadata

- id: DE-002
- domain: general
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: cdn, stale-assets, cache-control, deploy, frontend

## Ground Truth

- root_cause: The CDN is caching a non-versioned JavaScript asset path across deploys.
- why_it_happens: The same URL continues to point to a new bundle while the CDN still treats the old response as fresh.
- accepted_fix: Use content-hashed asset filenames or explicit CDN invalidation so deploys cannot serve stale JS by the same URL.
- rejected_fix_patterns:
  - blame React state
  - reduce app retries
  - tell users to hard refresh as the product fix

## Evidence Signals

- strongest_signal: Origin has the new asset while the CDN edge continues serving the old response
- strongest_alternative_explanation: Browser cache only
- why_alternative_is_wrong: Bypassing the CDN changes the result immediately while the same client still sees stale CDN content

## Scoring Notes

- full_credit_conditions:
  - identifies CDN cache with non-versioned asset path
  - proposes hashed assets or purge strategy
  - verification includes origin vs CDN comparison
- partial_credit_conditions:
  - spots stale cache but not the asset versioning issue
- fail_conditions:
  - blames backend deploy
  - proposes only shorter TTL without cache-busting strategy
