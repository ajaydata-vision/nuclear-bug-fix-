# Evaluator

## Metadata

- id: IN-012
- domain: integration
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: etl, data-pipeline, silent-drop, validation, null, missing-rows

## Ground Truth

- root_cause: isin() returns False for null values, silently excluding rows where category is null from the output.
- why_it_happens: pandas isin() does not treat null as a match for any value in the list. Null-category rows are filtered out without any error or warning.
- accepted_fix: Explicitly handle nulls: df[df['category'].isin(allowed_categories) | df['category'].isna()] to keep null rows, or log and route them separately.
- rejected_fix_patterns:
  - fill nulls with a default category before the filter
  - ignore the dropped rows as invalid data without investigating

## Evidence Signals

- strongest_signal: Row count mismatch exactly equals rows with null category; isin() silently excludes nulls
- strongest_alternative_explanation: Database write constraint rejecting rows
- why_alternative_is_wrong: Row count is already reduced before the database write; the drop happens in the pandas filter step

## Scoring Notes

- full_credit_conditions:
  - identifies isin() dropping nulls silently
  - proposes handling nulls explicitly with isna()
  - confirms by counting null-category rows in source
- partial_credit_conditions:
  - identifies the filter as the drop point but proposes only filling nulls with a default
- fail_conditions:
  - blames database write failures
  - adds a count assertion at the end without identifying the drop point
