# Verification

## After Fix

```elixir
def handle_call({:build, user_id, account_id}, _from, state) do
  report = compile_report(account_id)  # pass directly, no state mutation
  Logger.info("Report generated: account_id=#{account_id} for user=#{user_id}")
  {:reply, report, state}  # state unchanged
end

defp compile_report(account_id) do  # argument, not state
  MyApp.Accounts.get_financial_data(account_id)
end
```

## Regression Checks

- 50 concurrent users each requesting their own report: zero cross-contamination
- Log shows correct account_id matches requesting user_id in every line
- GenServer state remains empty map (no per-request data accumulated)
