# Evaluator

## Metadata

- id: IN-008
- domain: integration
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: schema-drift, api-contract, breaking-change, microservice, json

## Ground Truth

- root_cause: The downstream service renamed the user field to account in its response, breaking callers that expect the original field name.
- why_it_happens: Field renaming is a breaking API change even when the semantics are equivalent. Callers depending on the original field name receive undefined and crash.
- accepted_fix: Short term: update the caller to use response.data.account.id. Long term: downstream should version the API or maintain backward compatibility. Add contract testing between services.
- rejected_fix_patterns:
  - add try/catch around the field access to suppress the error
  - switch to any-type TypeScript to avoid the type error

## Evidence Signals

- strongest_signal: Field exists in old response but not new; TypeError points to renamed field; correlates with downstream deployment
- strongest_alternative_explanation: Network error causing partial response
- why_alternative_is_wrong: Response is 200 with full body; field is present but under a different key as confirmed by logging the full response

## Scoring Notes

- full_credit_conditions:
  - identifies field renamed in downstream response
  - proposes updating caller and adding contract tests
  - explains field rename as breaking change
- partial_credit_conditions:
  - updates the caller field name without addressing the lack of contract testing
- fail_conditions:
  - adds error suppression without fixing the field name
  - blames the downstream team without providing a fix
