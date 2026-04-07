# Evaluator

## Metadata

- id: EL-003
- domain: elixir-phoenix
- pattern: Stale PID after supervisor restart
- track: intermittent-race
- difficulty: medium
- determinism: intermittent
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: genserver, pid, stale, supervisor, restart, noproc, process-registry

## Ground Truth

- root_cause: `SessionCache.start_link` resolves `MyApp.SessionStore`'s PID once at startup via `Process.whereis/1` and stores it in state. When `SessionStore` crashes and the supervisor restarts it, the new process has a new PID. `SessionCache` still holds the old PID in `state.store_pid`. Calls to the dead old PID raise `noproc`.
- why_it_happens: PIDs are process identifiers for a specific process instance. Supervisor restart creates a new process instance with a new PID. Cached PIDs always go stale when a process restarts. The correct approach is to resolve the PID via the registered name at every call — the registry always points to the current live process.
- accepted_fix: Remove `store_pid` from state. Call `GenServer.call(MyApp.SessionStore, ...)` directly using the registered name — this resolves the current PID at every call.
- rejected_fix_patterns:
  - add a Process.monitor in start_link and handle :DOWN to refresh (works but overly complex)
  - restart SessionCache when SessionStore restarts (creates cascade restarts)
  - catch the noproc error and retry (masks the bug, still uses stale PID)

## Evidence Signals

- strongest_signal: `Process.whereis(MyApp.SessionStore)` called once at `start_link` and stored in state; `SessionStore restarted by supervisor` in logs; error correlates with hourly restarts
- pathognomonic_prove: `Process.alive?(state.store_pid)` → false AND `Process.whereis(MyApp.SessionStore)` returns a different PID → stale reference confirmed
- strongest_alternative_explanation: SessionStore is actually crashing during the failing call
- why_alternative_is_wrong: Logs show SessionStore alive 2ms after the error; restarts are hourly and unrelated to the failing request

## Scoring Notes

- full_credit_conditions:
  - identifies cached PID from start_link going stale after supervisor restart
  - explains that supervisor restart creates a new PID
  - fix calls GenServer.call(MyApp.SessionStore, ...) by name, not cached PID
  - mentions Process.alive? Prove
- partial_credit_conditions:
  - identifies PID staleness but suggests monitoring instead of using registered name
- fail_conditions:
  - suggests increasing supervisor restart intensity
  - blames the memory leak in SessionStore as the primary bug to fix
