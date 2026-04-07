# Evaluator

## Metadata

- id: EL-014
- domain: elixir-phoenix
- pattern: Oban wrong return value
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: oban, return-value, with, silent-failure, perform, completed

## Ground Truth

- root_cause: The `with` chain short-circuits before reaching `Notifications.push/2`. The result of the `with` expression (an error tuple like `{:error, :order_not_found}` or `{:error, :user_inactive}`) is assigned to `result` but then discarded — the function always returns `:ok` on the next line. Oban sees `:ok` and marks the job `completed`. The `with` chain exits early (order not shipped yet, user inactive, or no primary device), but `:ok` is returned regardless, so Oban never retries.
- why_it_happens: The bare `:ok` after the `with` block is always the return value of `perform/1`. The `with` expression's return value is stored in `result` but `result` is never used. This is the same pattern as EL-004 but inside an Oban worker — the consequence is that Oban marks the job completed (`:ok` returned) when it should have been retried (`{:error, reason}`) or cancelled (`{:cancel, reason}`).
- accepted_fix: Return the `result` from the `with` expression directly, or use an `else` clause to map error cases to Oban return values.
- rejected_fix_patterns:
  - add more logging (would confirm the issue but not fix it)
  - increase max_attempts (irrelevant — job is marked completed, not retried)
  - check push notification service credentials (confirmed working in IEx)

## Evidence Signals

- strongest_signal: bare `:ok` after `with ... end`; `result` variable assigned but never used; job shows completed despite no notification sent
- pathognomonic_prove: `IO.inspect(result, label: "[OBAN-RETURN-PROVE] with result")` before the bare `:ok` — shows `{:error, :order_not_shipped}` or similar while job is marked completed
- strongest_alternative_explanation: Push notification service API key invalid in production
- why_alternative_is_wrong: IEx manual call works (same credentials); job completes instead of failing (if API key invalid, push would fail with error, not silently)

## Scoring Notes

- full_credit_conditions:
  - identifies bare :ok after with block discarding with chain return value
  - explains Oban marks job completed on :ok regardless of with result
  - fix returns result directly or uses else clause with {:error, reason} / {:cancel, reason}
  - mentions IO.inspect(result) as the Prove
- partial_credit_conditions:
  - identifies the :ok return issue but doesn't explain the with chain short-circuit
- fail_conditions:
  - blames push notification service
  - suggests checking Oban queue configuration
