# Verification

## After Fix

```elixir
def handle_call({:get, session_id}, _from, state) do
  result = GenServer.call(MyApp.SessionStore, {:fetch, session_id})  # by name
  {:reply, result, state}
end
```

Remove `store_pid` from state entirely. `start_link` no longer calls `Process.whereis`.

## Regression Checks

- SessionStore restarts: SessionCache continues to work without restart
- `Process.whereis(MyApp.SessionStore)` called before and after restart returns different PIDs — both work
- noproc errors: zero after fix, across 10 simulated SessionStore restarts
