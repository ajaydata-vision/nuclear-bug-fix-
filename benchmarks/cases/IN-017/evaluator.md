# Evaluator

## Metadata

- id: IN-017
- domain: integration
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: kubernetes, image-tag, rollout, stale-image, deploy

## Ground Truth

- root_cause: The deployment uses a mutable image tag with `IfNotPresent`, so pods can keep using cached old images.
- why_it_happens: A green rollout only confirms Kubernetes applied the spec, not that nodes pulled a fresh image digest.
- accepted_fix: Use immutable image tags or digests and force a rollout against the new artifact.
- rejected_fix_patterns:
  - blame the application code
  - restart only one pod without fixing the tagging strategy
  - assume rollout status proves new code is running

## Evidence Signals

- strongest_signal: `/version` still reports old code even though rollout is green
- strongest_alternative_explanation: CDN or browser cache is stale
- why_alternative_is_wrong: The stale version is reported directly by running pods inside the cluster

## Scoring Notes

- full_credit_conditions:
  - identifies mutable tag plus pull policy as the cause
  - proposes immutable tags or digest pinning
  - verification includes checking live pod versions
- partial_credit_conditions:
  - spots stale image issue but not the exact rollout mechanism
- fail_conditions:
  - blames app cache only
  - treats rollout status as definitive proof of new code
