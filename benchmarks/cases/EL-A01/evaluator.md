# Evaluator

## Metadata

- id: EL-A01
- domain: elixir-phoenix
- pattern: GenServer deadlock (production-constrained Prove)
- track: adversarial
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: genserver, deadlock, production, iex, sys.get_state, constraint, proof

## Ground Truth

- root_cause: Identical to EL-001 — GenServer.call inside handle_call on same process causes mailbox deadlock.
- production_safe_prove:
  Without IEx, :sys.get_state is unavailable. The production-safe Prove uses:
  1. Log pattern: GenServer.call timeout error appears EXACTLY when count >= 100 threshold is hit — deterministic correlation between the threshold and the timeout
  2. Code analysis: `MyApp.RateLimiter.reset(user_id)` inside `handle_call` expands to `GenServer.call(__MODULE__, {:reset, user_id})` — this is visible from the source code alone and is definitionally a self-call deadlock
  3. Deploy a temporary logging Prove: add `Logger.error("[DEADLOCK-PROVE] handle_call calling reset — self-call about to deadlock")` immediately before `MyApp.RateLimiter.reset(user_id)` and deploy. If this log appears immediately before each timeout error, the Prove is complete.
  4. The supervisor restart log pair ("terminating" + "Child started") appearing only after the timeout confirms the GenServer died during the deadlocked call — not before it.

- why_iex_prove_not_required: The code contains a definitional deadlock — `GenServer.call(__MODULE__, ...)` from inside `handle_call`. No runtime proof is needed to establish this as the cause; the static code analysis IS the proof. The runtime evidence (timeout at threshold=100, supervisor restart) is corroborating evidence.

- accepted_fix: Inline the reset logic inside handle_call — remove the re-entrant GenServer.call(__MODULE__, :reset). Same fix as EL-001.
- confidence_without_iex: HIGH — code analysis + log correlation is sufficient. :sys.get_state is the runtime confirmation tool, not the only proof. A code review finding `GenServer.call` inside `handle_call` on the same module is unambiguous.

## Scoring Notes

- full_credit_conditions:
  - identifies that :sys.get_state requires IEx and is unavailable in this constraint
  - provides production-safe alternative Prove (log correlation + code analysis OR temporary log deploy)
  - correctly states HIGH confidence is achievable from code analysis alone
  - does NOT say confidence is reduced to MEDIUM just because IEx is unavailable
  - explains that the code contains a definitional deadlock (GenServer.call on same module from handle_call)
- partial_credit_conditions:
  - provides the correct root cause but says confidence must be MEDIUM without :sys.get_state
  - provides :sys.get_state instructions despite the production constraint
- fail_conditions:
  - says it cannot be diagnosed without IEx access
  - provides only the IEx Prove without acknowledging the constraint
  - reduces confidence to LOW because of the missing runtime tool
