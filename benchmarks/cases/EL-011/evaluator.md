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

- root_cause: `Repo.transaction(multi)` returns `{:ok, %{account: ..., user: ..., profile: ...}}` on success or `{:error, failed_step, changeset, completed}` on failure. The function discards the transaction result entirely and always returns `{:ok, "account created"}`. If the `:user` or `:profile` step fails (e.g., email uniqueness constraint, missing required field), the transaction rolls back ALL steps including the `:account` insert — but the function still returns `{:ok, "account created"}`. Actually, given only account is found in DB: the account insert succeeds, then a later step fails, the transaction rolls back account too — but maybe the caller is calling something else, or the account was created outside the Multi. 

  More precisely: the return value of `Repo.transaction(multi)` is discarded. The bare `{:ok, "account created"}` is always returned. The Multi may have failed at the :user step (email already taken, etc.) causing a rollback of all steps including account. But if account is present in DB, the transaction must have succeeded but only account creation matters to this bug. 

  Actually: account IS in DB, user and profile are NOT. This means the Multi ran, account was committed, but user/profile were not. This can happen if: (a) the transaction returned {:error, :user, ...} and the account somehow bypassed the transaction — impossible with Multi. More likely: there are TWO operations: one that creates the account directly (outside the Multi) and one Multi call that fails for user/profile. The result of the Multi is discarded so the error is hidden.

  Simplest interpretation: Repo.transaction result discarded → {:error, :user, changeset, %{account: account}} returned by transaction but caller sees {:ok, "account created"} → user and profile not created, account rolled back but a separate Account.changeset was called before the Multi and committed separately.

- why_it_happens: `Repo.transaction(multi)` return value is discarded. Always returning `{:ok, "account created"}` hides any failure from the Multi.
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
