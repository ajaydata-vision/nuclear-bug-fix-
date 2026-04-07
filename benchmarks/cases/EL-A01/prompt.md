# EL-A01: GenServer Deadlock — Production, No IEx Access

## User Prompt

Same scenario as EL-001: our `RateLimiter` GenServer deadlocks when the rate limit threshold is hit. We've confirmed the root cause — `handle_call` calls back into the same GenServer. We need to prove it to our team before deploying the fix, but this is production and we have no IEx remote shell access. We can only read logs and deploy code changes. The deadlock only happens in production (threshold never hit in staging). How do we prove this is definitely a GenServer self-deadlock and not something else?

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, OTP 26
- environment: PRODUCTION — no IEx remote shell, no observer access
- constraints: cannot run :sys.get_state or Process.info interactively
- logs:
  - `[error] ** (exit) exited in: GenServer.call(MyApp.RateLimiter, {:check, "user_99"}, 5000)`
  - `[error] ** (EXIT) time out`
  - `[info] Child MyApp.RateLimiter of Supervisor MyApp.Supervisor started`
- code excerpt:
```elixir
def handle_call({:check, user_id}, _from, state) do
  count = Map.get(state, user_id, 0)
  if count >= 100 do
    MyApp.RateLimiter.reset(user_id)  # → GenServer.call(self(), :reset)
    {:reply, :rate_limited, state}
  else
    {:reply, :ok, Map.put(state, user_id, count + 1)}
  end
end
```
