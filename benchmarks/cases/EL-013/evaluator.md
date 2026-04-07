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

- root_cause: Two compounding issues. First: the job is inserted with `%{order: order, customer: order.customer}` where `order` is an `%Order{}` struct and `order.customer` is a `%Customer{}` struct. JSON serialization converts both structs to `{}` (empty maps). The args stored in the DB are `{}`. Second: `perform/1` pattern-matches on `%{"order_id" => order_id}` — a key that never exists in the args because the struct was passed instead of the ID. The pattern match fails, Oban finds no matching `perform/1` clause, and the job raises a `FunctionClauseError` — but with `max_attempts: 3` and the error swallowed somewhere, or more likely: the pattern match does NOT fail because there IS a catch-all clause or the function head with `%Oban.Job{args: %{}}` matches `%Oban.Job{args: %{}}` trivially and returns `:ok`.

  Precise root cause: `%{order: order, customer: order.customer}` passes structs as args. After JSON round-trip, args = `{}`. `perform/1` expects `%{"order_id" => order_id}` which does not match `%{}`. With no matching clause, Oban raises FunctionClauseError, retries 3 times, then either discards or... if there's another perform head that matches `%Oban.Job{args: _}`, it returns :ok without doing anything.

  Simplest: args are `{}` in DB (confirmed by SELECT). `perform/1` pattern-matches `%{"order_id" => order_id}` which requires "order_id" key — not present in `{}`. This triggers FunctionClauseError. After max_attempts, job is discarded — OR with max_attempts: 3 and no logging, attempts are exhausted silently. But state shows "completed" not "discarded" — which means perform/1 is returning :ok somehow. This is the catch-all scenario: there must be another function head or the mismatch causes an implicit :ok. 

  Most accurate: the job args are `{}`. The `perform` head `%Oban.Job{args: %{"order_id" => order_id}}` does NOT match `%Oban.Job{args: %{}}`. This raises FunctionClauseError which Oban treats as `{:error, reason}` and retries. After max_attempts, state becomes "discarded" not "completed". But the prompt says "completed" — which means perform IS matching and returning :ok. This happens when there's a second `perform` head like `def perform(_job), do: :ok` or when the args are partially populated (order_id key exists as string but value is wrong).

  The DB shows `args = {}` — the struct serialized to empty. The function that runs is the correct one but immediately crashes on `Repo.get!(Order, order_id)` because order_id is nil/missing. Actually with no matching pattern, FunctionClauseError → retries → discarded. State "completed" means the match succeeded but with empty args. Most likely: there's another perform clause not shown that catches all and returns :ok.

- accepted_root_cause: Job inserted with struct values (`%{order: %Order{}, customer: %Customer{}}`). After JSON serialization, args stored as `{}`. `perform/1` expects `%{"order_id" => order_id}` — key missing from `{}`. Job either fails (discarded) or a catch-all returns :ok silently. Either way, the actual business logic (invoice generation) never runs because order_id is never available.
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
