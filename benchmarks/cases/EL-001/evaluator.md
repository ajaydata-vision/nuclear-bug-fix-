# Evaluator

## Metadata

- id: EL-001
- domain: elixir-phoenix
- pattern: GenServer deadlock
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: genserver, deadlock, handle_call, self-call, otp, mailbox

## Ground Truth

- root_cause: `handle_call({:check, ...})` calls `MyApp.RateLimiter.reset(user_id)`, which calls `GenServer.call(__MODULE__, {:reset, user_id})` on the same process. The GenServer is already processing the `:check` call — its mailbox is locked. The `:reset` call is placed in the mailbox and waits for the current call to finish, which cannot finish because it is waiting for `:reset`. Classic self-deadlock.
- why_it_happens: GenServer serialises all messages through a single mailbox. A `GenServer.call` from inside `handle_call` on the same process sends a message to that process's own mailbox and then blocks the caller (which IS the GenServer) waiting for a reply that can never arrive because the GenServer is the one blocked.
- accepted_fix: Remove the `GenServer.call` from inside `handle_call`. Either inline the reset logic directly, or use `GenServer.cast` for the reset (fire-and-forget). Best fix: inline the Map.delete inside the `:check` handler when the limit is hit.
- rejected_fix_patterns:
  - increase the call timeout to 30_000 (still deadlocks, just waits longer)
  - wrap the reset in Task.async (creates a new call from a different process — breaks the deadlock but adds complexity unnecessarily)
  - use a database instead of GenServer state (changes the architecture, doesn't explain the bug)

## Evidence Signals

- strongest_signal: `GenServer.call(__MODULE__, {:reset, user_id})` appears inside `handle_call` on the same module; timeout errors appear exactly when the rate limit threshold is hit (count >= 100 triggers the reset path)
- pathognomonic_prove: `Task.async(fn -> :sys.get_state(Process.whereis(MyApp.RateLimiter)) end) |> Task.yield(2_000)` returns `nil` (times out) — mailbox blocked
- strongest_alternative_explanation: External process holding a lock on the GenServer
- why_alternative_is_wrong: Code shows no external locks; the issue triggers deterministically at count >= 100; restarting fixes it (no external state involved)

## Scoring Notes

- full_credit_conditions:
  - identifies `GenServer.call(__MODULE__, :reset)` inside `handle_call` as the cause
  - explains the mailbox self-deadlock mechanism
  - provides fix that removes the re-entrant call (inline logic or cast)
  - mentions the :sys.get_state Prove or equivalent mailbox inspection
- partial_credit_conditions:
  - identifies a deadlock but does not explain the self-call mechanism
  - identifies the timeout but suggests increasing it as the fix
- fail_conditions:
  - blames network timeout or client-side issue
  - suggests restarting the process as the fix (not root cause)
  - misidentifies as a race condition between two different processes
