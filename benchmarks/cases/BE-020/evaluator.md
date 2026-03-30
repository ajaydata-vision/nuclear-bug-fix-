# Evaluator

## Metadata

- id: BE-020
- domain: backend
- track: deploy-env
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: replica-lag, read-after-write, postgres, consistency

## Ground Truth

- root_cause: The immediate read is routed to a replica that has not yet caught up with the primary write.
- why_it_happens: Replication lag makes the post-write read observe stale state.
- accepted_fix: Route read-after-write requests to primary or guarantee read-your-writes consistency for this flow.
- rejected_fix_patterns:
  - add arbitrary sleep as the real fix
  - blame transaction rollback
  - blame UI cache without addressing replica routing

## Evidence Signals

- strongest_signal: Primary shows new value immediately while replica returns old value and later catches up
- strongest_alternative_explanation: Application-level cache is stale
- why_alternative_is_wrong: The stale read correlates specifically with replica routing and disappears after replication delay

## Scoring Notes

- full_credit_conditions:
  - names replica lag or read routing explicitly
  - proposes primary read or read-your-writes consistency
  - verification includes immediate read after write
- partial_credit_conditions:
  - identifies stale read but blames caching generically
- fail_conditions:
  - proposes only retry loops or sleeps
  - misses the primary/replica split
