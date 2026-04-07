# EL-001: GenServer.call Times Out — Request Hangs Forever

## User Prompt

Our Phoenix app has a `RateLimiter` GenServer that tracks API request counts per user. The endpoint `/api/data` calls `RateLimiter.check_and_increment(user_id)` to check the rate limit before processing. Under normal usage it works fine. But occasionally a request just hangs and never completes — the client gets a 5-second timeout. After that, the rate limiter stops working for everyone until we restart the server.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, OTP 26
- environment: production, single node, ~50 req/s
- logs:
  - `[error] GenServer MyApp.RateLimiter terminating`
  - `** (stop) exited in: GenServer.call(MyApp.RateLimiter, {:check, "user_99"}, 5000)`
  - `** (EXIT) time out`
  - After restart: rate limiter works again immediately
- code excerpt:
```elixir
defmodule MyApp.RateLimiter do
  use GenServer

  def check_and_increment(user_id) do
    GenServer.call(__MODULE__, {:check, user_id})
  end

  def reset(user_id) do
    GenServer.call(__MODULE__, {:reset, user_id})
  end

  def handle_call({:check, user_id}, _from, state) do
    count = Map.get(state, user_id, 0)
    if count >= 100 do
      # Reset and log for auditing
      MyApp.RateLimiter.reset(user_id)
      {:reply, :rate_limited, state}
    else
      {:reply, :ok, Map.put(state, user_id, count + 1)}
    end
  end

  def handle_call({:reset, user_id}, _from, state) do
    {:reply, :ok, Map.delete(state, user_id)}
  end
end
```
- reproduction:
  1. Make 100 API requests for a single user (hitting the rate limit)
  2. The 101st request hangs for 5 seconds then times out
  3. All subsequent requests to the rate limiter also hang
