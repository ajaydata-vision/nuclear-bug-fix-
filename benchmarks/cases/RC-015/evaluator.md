# Evaluator

## Metadata

- id: RC-015
- domain: frontend
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react, optimistic-update, race, slow-network, state-sync, mutation

## Ground Truth

- root_cause: Multiple in-flight mutations each apply an optimistic increment independently. Out-of-order server responses cause the optimistic and actual states to desynchronise temporarily.
- why_it_happens: Optimistic updates accumulate without tracking in-flight mutations. When responses arrive out of order, each onSuccess overwrites state without accounting for other pending mutations.
- accepted_fix: Implement TanStack Query's recommended optimistic update pattern: save previous state in onMutate, roll back on onError, and let onSettled invalidate the query to refetch the authoritative server state.
- rejected_fix_patterns:
  - debounce the like button to prevent rapid clicks
  - disable optimistic updates entirely

## Evidence Signals

- strongest_signal: Flash of wrong count followed by correction; only on slow networks where multiple mutations are in-flight simultaneously
- strongest_alternative_explanation: Server returning wrong like count
- why_alternative_is_wrong: The count corrects itself when the server response arrives, proving the server is authoritative; the flash is a client-side optimistic state issue

## Scoring Notes

- full_credit_conditions:
  - identifies out-of-order optimistic updates as the cause
  - proposes onMutate save + onError rollback + onSettled invalidate pattern
  - explains in-flight mutation tracking
- partial_credit_conditions:
  - identifies the race but proposes only disabling optimistic updates
- fail_conditions:
  - debounces the button without fixing the state management
  - ignores the race because it self-corrects
