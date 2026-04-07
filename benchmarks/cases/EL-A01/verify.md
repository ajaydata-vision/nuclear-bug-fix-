# Verification

## Production-Safe Proof Strategy

1. Code analysis: confirm `GenServer.call(__MODULE__, {:reset, ...})` appears inside `handle_call` — this IS the proof
2. Log correlation: timeout errors appear only when count >= 100 (the branch that calls reset)
3. Optional deploy confirmation: add `Logger.error("[DEADLOCK-PROVE]")` before the self-call, deploy, observe it appears before each timeout

## Fix Deployment

Same as EL-001 — inline the reset logic, no re-entrant call needed.
Regression: after deploy, no timeout errors at count >= 100.
