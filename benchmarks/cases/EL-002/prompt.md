# EL-002: Users See Each Other's Reports Under Concurrent Load

## User Prompt

Our Phoenix app has a `ReportBuilder` GenServer that compiles financial reports on demand. Users click "Generate Report" and the GenServer builds the report for their account. Works perfectly in testing. In production with multiple users, User A's report occasionally shows User B's financial data. Sessions are correct — we verified the user IDs in the session. The data is wrong at the report level only.

## Context Provided To The Skill

- stack: Elixir 1.15, Phoenix 1.7.8, OTP 26
- environment: production, 20-50 concurrent users
- logs:
  - `[info] Report requested by user_id=1042`
  - `[info] Report generated: account_id=9981 revenue=84200`
  - `[info] Report requested by user_id=2087`
  - `[info] Report delivered to user_id=2087 account_id=9981` ← wrong account
- code excerpt:
```elixir
defmodule MyApp.ReportBuilder do
  use GenServer

  def build_report(user_id, account_id) do
    GenServer.call(__MODULE__, {:build, user_id, account_id})
  end

  def handle_call({:build, user_id, account_id}, _from, state) do
    state = Map.put(state, :current_account, account_id)
    state = Map.put(state, :current_user, user_id)
    report = compile_report(state)
    Logger.info("Report generated: account_id=#{state.current_account}")
    {:reply, report, state}
  end

  defp compile_report(state) do
    MyApp.Accounts.get_financial_data(state.current_account)
  end
end
```
- reproduction:
  1. Two users request reports simultaneously
  2. User B's report contains User A's account data
  3. Never reproduces with one user at a time
