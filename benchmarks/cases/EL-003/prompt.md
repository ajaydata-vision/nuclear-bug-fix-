# EL-003: Intermittent noproc Error on Calls to Running GenServer

## User Prompt

We have a `SessionStore` GenServer registered by name. Most requests work fine. But intermittently — maybe 1 in 200 requests — we get `** (EXIT) no process: the process is not alive` when calling it. The GenServer IS alive — we can see it in observer and it responds to other requests immediately before and after the error. The error appears randomly, not tied to any specific user or action.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.10, OTP 26
- environment: production, deployed via releases
- logs:
  - `[error] ** (EXIT) no process: the process is not alive and no process is registered under this name`
  - `[error] Process MyApp.SessionStore is alive: true` (logged 2ms after the error)
  - `[info] SessionStore restarted by supervisor` (appears in logs ~hourly)
- code excerpt:
```elixir
defmodule MyApp.SessionCache do
  use GenServer

  def start_link(_) do
    store_pid = Process.whereis(MyApp.SessionStore)
    GenServer.start_link(__MODULE__, %{store_pid: store_pid}, name: __MODULE__)
  end

  def get_session(session_id) do
    GenServer.call(__MODULE__, {:get, session_id})
  end

  def handle_call({:get, session_id}, _from, state) do
    result = GenServer.call(state.store_pid, {:fetch, session_id})
    {:reply, result, state}
  end
end
```
- reproduction:
  1. SessionStore crashes and is restarted by supervisor (happens hourly due to a memory leak)
  2. SessionCache continues to use the old PID stored at startup
  3. Calls to the old PID fail with noproc

