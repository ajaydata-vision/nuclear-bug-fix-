# Evaluator

## Metadata

- id: EL-011
- domain: elixir-phoenix
- pattern: Ecto.Multi transaction rollback invisible
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: ecto, multi, transaction, rollback, pattern-match, return-value

## Ground Truth

- root_cause: The return value of `Repo.transaction(multi)` is discarded. The function always returns `{:ok, "account created"}` regardless of whether the transaction succeeded or failed. When the `:user` step fails (email uniqueness constraint, missing required field, etc.), `Repo.transaction` returns `{:error, :user, changeset, %{account: account}}` and rolls back ALL steps — including the account insert. The caller receives `{:ok, "account created"}` and concludes success. The account, user, and profile are all absent from the database.
- why_it_happens: `Repo.transaction` return value must be pattern-matched to know whether the transaction succeeded. A bare `{:ok, "account created"}` after the `Repo.transaction` call — without piping or matching the result — discards both the success data and any error information. Ecto.Multi is all-or-nothing: if any step fails, all completed steps are rolled back atomically.
- accepted_fix: Pattern-match on `Repo.transaction(multi)` result and return the actual outcome.
- rejected_fix_patterns:
  - use bang functions inside Multi (raises exceptions — harder to handle)
  - separate the inserts into individual Repo.insert calls (loses atomicity)

## Evidence Signals

- strongest_signal: `Repo.transaction(multi)` result is not pattern-matched; bare `{:ok, "account created"}` always returned
- pathognomonic_prove: `IO.inspect(Repo.transaction(multi), label: "[MULTI-PROVE] transaction result")` — shows `{:error, :user, %Ecto.Changeset{errors: [email: ...]}, %{account: #Account<>}}`
- strongest_alternative_explanation: Profile changeset has a default value bug causing it to save as nil
- why_alternative_is_wrong: Profile not in DB at all (not saved with nil values); rollback is confirmed by the all-or-nothing behavior of transactions

## Scoring Notes

- full_credit_conditions:
  - identifies Repo.transaction result being discarded
  - identifies always-returning {:ok, "account created"} as hiding the error
  - fix pattern-matches transaction result and propagates {:error, step, changeset, _}
  - mentions IO.inspect(Repo.transaction(multi)) as the Prove
- partial_credit_conditions:
  - identifies missing error handling but suggests try/rescue instead
- fail_conditions:
  - blames the Profile changeset without examining the transaction result
  - suggests adding DB constraints
