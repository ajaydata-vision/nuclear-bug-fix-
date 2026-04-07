# Verification

## Before Fix

1. Start RateLimiter with the buggy code
2. Send 100 requests for user "test_user" (hits the threshold)
3. Send 101st request — observe it hangs for 5 seconds then times out
4. Send any request after — also hangs (GenServer mailbox stuck)

## After Fix (inline reset logic)

```elixir
def handle_call({:check, user_id}, _from, state) do
  count = Map.get(state, user_id, 0)
  if count >= 100 do
    {:reply, :rate_limited, Map.delete(state, user_id)}  # inline, no re-entrant call
  else
    {:reply, :ok, Map.put(state, user_id, count + 1)}
  end
end
```

## Regression Checks

- 100 requests for same user: all return :ok
- 101st request: returns :rate_limited immediately (no hang)
- 102nd request: returns :ok (state was cleared correctly)
- Concurrent users: each user's count tracked independently
