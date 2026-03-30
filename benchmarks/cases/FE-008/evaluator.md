# Evaluator

## Metadata

- id: FE-008
- domain: frontend
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react, async-race, stale-response, fetch, search

## Ground Truth

- root_cause: Older or slower fetch responses are not cancelled or ignored, so a
  later-resolving response overwrites newer UI state.
- why_it_happens: Each query change starts a new fetch, but all completions call
  `setResults` without validating request freshness.
- accepted_fix: Abort stale requests or guard updates with a request ID / latest-query check.
- rejected_fix_patterns:
  - add arbitrary debounce as the only fix
  - blame backend data quality
  - move fetch outside the effect without freshness control

## Evidence Signals

- strongest_signal: The UI is overwritten by the slower response, not by a bad initial render
- strongest_alternative_explanation: The backend sometimes returns empty data incorrectly
- why_alternative_is_wrong: The direct API call is stable and the failure pattern depends on rapid query changes

## Scoring Notes

- full_credit_conditions:
  - identifies race between overlapping requests
  - proposes cancellation or freshness guard
  - verification includes rapid typing or mocked delayed responses
- partial_credit_conditions:
  - spots a race but proposes debounce only
- fail_conditions:
  - blames React rendering
  - blames the API without addressing overlapping requests
