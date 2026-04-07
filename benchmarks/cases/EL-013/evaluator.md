# Evaluator

## Metadata

- id: EL-013
- domain: elixir-phoenix
- pattern: Oban struct-in-args
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: oban, struct, args, json, serialization, pattern-match, string-keys

## Ground Truth

- root_cause: The job is inserted with struct values — `%{order: order, customer: order.customer}` where both `order` and `order.customer` are Elixir structs (`%Order{}`, `%Customer{}`). JSON serialization converts structs to empty maps `{}`. The args column in `oban_jobs` stores `{}` instead of `{"order_id": 42, ...}`. The `perform/1` function expects `%{"order_id" => order_id}` — a key that was never stored. Job state shows `completed` because the prompt's implied context includes an unshown catch-all `perform` clause (or the framework matched and returned `:ok` without business logic), but in all cases the invoice generation never executes because `order_id` is unavailable.
- accepted_root_cause: Structs-in-args. `%{order: %Order{}, customer: %Customer{}}` serializes to `{}`. The fix is to insert plain scalar IDs only: `%{order_id: order.id}`.
- accepted_fix: Insert only plain scalar values: `%{order_id: order.id}`. Pattern-match string keys in perform: `%{"order_id" => order_id}`.
- rejected_fix_patterns:
  - Jason.encode the struct before inserting (still loses type information, fragile)
  - store the entire order as JSON string in args (large args, not idiomatic)

## Evidence Signals

- strongest_signal: `SELECT args FROM oban_jobs` shows `{}` for all rows; job insertion passes structs (`order:` and `customer:` keys with struct values)
- pathognomonic_prove: DB query shows args = `{}` — struct serialized to empty map; this is pathognomonic for struct-in-args
- strongest_alternative_explanation: Mailer or PDF generator silently failing
- why_alternative_is_wrong: IEx manual run works (proves Mailer/PDF are fine); args = {} in DB proves the issue is at the arg serialization level before any business logic runs

## Scoring Notes

- full_credit_conditions:
  - identifies struct-in-args causing JSON serialization to empty map
  - explains that Elixir structs serialize to {} in JSON
  - fix inserts %{order_id: order.id} with plain scalar value
  - fix uses string key pattern match %{"order_id" => order_id} in perform/1
  - references SELECT args FROM oban_jobs showing {} as the Prove
- partial_credit_conditions:
  - identifies the args problem but doesn't explain JSON serialization mechanism
  - fixes perform/1 pattern match but doesn't fix the insertion
- fail_conditions:
  - blames the Mailer or PDF generator
  - suggests increasing max_attempts
