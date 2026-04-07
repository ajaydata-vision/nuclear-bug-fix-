# Evaluator

## Metadata

- id: EL-005
- domain: elixir-phoenix
- pattern: LiveView silent form save
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: liveview, form, changeset, handle_event, silent-failure, pattern-match

## Ground Truth

- root_cause: The `case` expression in `handle_event` only pattern-matches `{:ok, updated_user}`. When `Accounts.update_profile/2` returns `{:error, changeset}` (validation failure or DB error), the case expression has no matching clause and raises a `CaseClauseError`. LiveView catches this crash and recovers the socket — the user sees the form reload with no error. The changeset errors exist but are never assigned to the socket for display.
- why_it_happens: LiveView wraps handle_event execution and recovers from crashes silently (from the user's perspective) to maintain the connection. The developer sees no error in logs if Logger level is above debug. The `{:error, changeset}` branch is simply unhandled — the CaseClauseError crash causes LiveView to re-render from the last known good socket state.
- accepted_fix: Add the `{:error, changeset}` branch to the case and assign the changeset back to the form.
- rejected_fix_patterns:
  - use a bang function Accounts.update_profile!/2 (raises on error — worse, crashes the LiveView)
  - add a catch-all _ -> {:noreply, socket} (hides the error, still doesn't show validation errors)

## Evidence Signals

- strongest_signal: `case` only matches `{:ok, _}` — `{:error, changeset}` branch missing
- pathognomonic_prove: Add `IO.inspect(Accounts.update_profile(user, params["user"]), label: "[SILENT-SAVE-PROVE]")` in handle_event — output shows `{:error, #Ecto.Changeset<errors: [name: {"can't be blank", ...}]>}` while user sees no error
- strongest_alternative_explanation: params["user"] is nil or wrong key
- why_alternative_is_wrong: DB record unchanged (update attempted but failed validation); if params were nil it would crash with a different error visible in logs

## Scoring Notes

- full_credit_conditions:
  - identifies missing {:error, changeset} branch in case expression
  - explains LiveView crash recovery hides the CaseClauseError from user
  - fix adds {:error, changeset} -> {:noreply, assign(socket, :form, to_form(changeset))}
  - mentions IO.inspect on update result as Prove
- partial_credit_conditions:
  - identifies missing error branch but does not explain LiveView crash recovery
- fail_conditions:
  - blames JavaScript or phx-submit wiring
  - suggests checking network tab without examining case expression
