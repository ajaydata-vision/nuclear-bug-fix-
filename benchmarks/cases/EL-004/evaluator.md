# Evaluator

## Metadata

- id: EL-004
- domain: elixir-phoenix
- pattern: with/1 chain silently returns wrong value
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: with, silent-failure, return-value, elixir-idiom, no-else

## Ground Truth

- root_cause: The bare `:ok` after the `with` block executes unconditionally regardless of whether the `with` chain succeeded or short-circuited. The `with ... do ... end` expression returns either `:ok` (success path) or the first non-matching value (short-circuit path). But then the function continues to the bare `:ok` on the next line — which is the actual return value of the function. The `with` block's return value is discarded. Additionally, if `Mailer.send_welcome` returns something other than `{:ok, _}` (e.g., `{:error, :config_missing}`), the `with` exits silently and the bare `:ok` still returns.
- why_it_happens: The bare `:ok` after `end` is always the last expression evaluated and always the return value of the function. The `with` block is evaluated for its side effects (creating user/workspace/sending email) but its return value is thrown away. If any step fails, the `with` exits early — the email is never sent — but the function still returns `:ok`.
- accepted_fix: Remove the bare `:ok` after the `with` block. Let the `with` expression be the function's return value. Add an `else` clause.
- rejected_fix_patterns:
  - wrap in try/rescue (no exceptions are raised — the issue is return value, not exceptions)
  - move email send outside the with (breaks the transactional intent)

## Evidence Signals

- strongest_signal: bare `:ok` on the line after `with ... do ... end` — always executes
- pathognomonic_prove: Add `|> IO.inspect(label: "[WITH-PROVE]")` after each `<-` step — identify which step prints last; if "Onboarding complete" never logs, the email step is short-circuiting
- strongest_alternative_explanation: Mailer configuration issue causing send_welcome to fail
- why_alternative_is_wrong: Mailer works in IEx isolation; if it failed, the with chain would short-circuit — which is exactly what's happening, AND the bare :ok hides it

## Scoring Notes

- full_credit_conditions:
  - identifies bare `:ok` after `with` block as the unconditional return value
  - explains that the `with` block's return value is discarded
  - fix removes bare `:ok` and adds `else` clause
  - mentions IO.inspect on each `<-` step as the Prove
- partial_credit_conditions:
  - identifies the bare `:ok` but does not explain why the email isn't sent
  - says to add error handling without explaining the discard mechanism
- fail_conditions:
  - blames Swoosh/mailer configuration without examining the with structure
  - suggests checking email provider logs without addressing the code bug
