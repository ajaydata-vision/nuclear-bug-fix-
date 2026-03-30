# Evaluator

## Metadata

- id: VE-007
- domain: version-external-intelligence
- track: regression-version
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: false
- tags: breaking-change, migration, mongoose, schema, data-loss, major-upgrade

## Ground Truth

- root_cause: Mongoose 7 changed the default behavior of sanitizeFilter and how null values are handled in updates. Explicit null values are now treated differently in certain query forms.
- why_it_happens: Mongoose 7.0 introduced a breaking change in how null field updates are applied when using schema defaults and $set. The behavior change was not prominently documented in the migration guide.
- accepted_fix: Use $set explicitly: { $set: { optionalNote: null } } or configure Mongoose with returnDocument and strict query options to restore v6 behavior.
- rejected_fix_patterns:
  - store empty string instead of null
  - add null checks in application code

## Evidence Signals

- strongest_signal: Behavior changed exactly on Mongoose major version upgrade; Mongoose 7 changelog or GitHub issues confirm the null update behavior change
- strongest_alternative_explanation: MongoDB rejecting null values
- why_alternative_is_wrong: MongoDB accepts null values; the issue is Mongoose's query transformation before sending to MongoDB

## Scoring Notes

- full_credit_conditions:
  - identifies Mongoose 7 null update behavior change
  - proposes explicit $set: { field: null }
  - references Mongoose 7 changelog or GitHub issue
- partial_credit_conditions:
  - identifies the Mongoose upgrade as the cause but proposes workarounds without the specific fix
- fail_conditions:
  - suggests MongoDB configuration change
  - switches to storing empty string without understanding the root cause
