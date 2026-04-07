# Evaluator

## Metadata

- id: EL-002
- domain: elixir-phoenix
- pattern: GenServer state contamination
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: genserver, state, contamination, concurrency, otp, per-request-state

## Ground Truth

- root_cause: `handle_call` stores `account_id` and `user_id` in the GenServer's persistent `state` map between calls. GenServer serialises calls (one at a time) but the state persists across calls. Call N sets `state.current_account = 9981`. Call N+1 starts before compile_report finishes — impossible since GenServer is serial. BUT: the state set by call N is the state passed to call N+1. If call N+1 arrives and somehow state.current_account was already set from a previous call that failed or was interrupted, the previous account bleeds in.

  More precisely: `state` is mutated and returned as the new state. If a fast sequence of calls occurs, the state.current_account from call N is the starting state for call N+1. The log shows account_id=9981 delivered to user_id=2087 — user 2087's call saw user 1042's account still in state.current_account from the previous call's state return.

- why_it_happens: Request-scoped data (current_account, current_user) is stored in the GenServer's persistent state instead of being passed as local function arguments. GenServer state persists across calls by design — it is meant for long-lived server data, not per-request context.

- accepted_fix: Pass account_id directly as a function argument to compile_report. Do not store per-request data in GenServer state.
- rejected_fix_patterns:
  - add a Map.delete(state, :current_account) at the end of handle_call (mitigates but doesn't fix race)
  - use Agent instead of GenServer (same problem — state persists)
  - add a mutex/lock (over-engineered — the fix is to not use state for per-request data)

## Evidence Signals

- strongest_signal: `state = Map.put(state, :current_account, account_id)` in handle_call stores request-scoped data in persistent GenServer state; bug only occurs under concurrency
- pathognomonic_prove: Add `IO.inspect(state.current_account, label: "[CONTAMINATION-PROVE] state.current_account at entry for account_id=#{account_id}")` at top of handle_call — under concurrent load, state.current_account will differ from the account_id in the message
- strongest_alternative_explanation: Phoenix session shared between users
- why_alternative_is_wrong: Logs confirm correct user IDs in sessions; contamination is at the report data level in the GenServer state

## Scoring Notes

- full_credit_conditions:
  - identifies storing per-request state (current_account/current_user) in GenServer state as the cause
  - explains that GenServer state persists between calls by design
  - fix passes account_id as function argument, not through state
- partial_credit_conditions:
  - identifies the bug location but proposes clearing state after each call
- fail_conditions:
  - blames Phoenix session management
  - suggests adding process isolation (each user gets own GenServer) without explaining root cause
