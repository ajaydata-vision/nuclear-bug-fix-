# Evaluator

## Metadata

- id: FE-013
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-router, query-params, navigation, useSearchParams

## Ground Truth

- root_cause: navigate('/search') replaces the entire URL including the query string. Existing params must be explicitly preserved.
- why_it_happens: React Router's navigate() uses the literal path string provided. It does not merge with existing search params. To keep params they must be read from location.search and re-applied.
- accepted_fix: Read current params and preserve them: navigate({ pathname: '/search', search: location.search }) or use useSearchParams to update only changed params.
- rejected_fix_patterns:
  - use window.history.pushState directly
  - store params in localStorage as workaround

## Evidence Signals

- strongest_signal: Params are present before navigation and absent after; navigate() receives no search string
- strongest_alternative_explanation: Server-side redirect stripping query params
- why_alternative_is_wrong: This is client-side navigation; the server is not involved

## Scoring Notes

- full_credit_conditions:
  - identifies navigate() not preserving existing search params
  - proposes passing search string explicitly or using useSearchParams
  - explains why navigate wipes params
- partial_credit_conditions:
  - identifies param loss but proposes storing params in state/storage instead
- fail_conditions:
  - blames React Router bug
  - suggests converting to hash-based params
