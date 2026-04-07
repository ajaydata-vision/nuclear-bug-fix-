# Elixir / Phoenix Bug Patterns

Covers: BEAM process model, OTP (GenServer/Supervisor), Phoenix LiveView,
Ecto (queries/transactions/constraints), Oban background jobs, Phoenix framework.
Each pattern: symptom → why → prove → fix.

---

## ⚠️ VISIBILITY PREREQUISITE — Run Before Any Prove

Elixir's BEAM supervisor **automatically restarts crashed processes in milliseconds**.
This means bugs disappear from the surface — the process restarts, one error line
appears in the log, and the developer sees a healthy system. The failure is real;
it is just hidden by recovery.

Before running any Prove below, confirm you can see failures:

```bash
# 1. Confirm Logger level is not filtering out crashes
grep "level:" config/dev.exs       # should be :debug
grep "level:" config/prod.exs      # :info hides debug output — check :error at minimum

# 2. Watch for the supervisor restart pair (both lines = crash + restart cycle)
grep "GenServer.*terminating" log/dev.log
grep "Child.*started" log/dev.log
# Same module in both lines = it is crashing and being restarted repeatedly

# 3. Confirm mix phx.server output is visible (not redirected to /dev/null)
# Crashes appear in the terminal running the server, not the browser console

# 4. For Oban jobs — jobs fail silently until max_attempts exhausted
# Check for discarded/retrying jobs before concluding the job never ran:
#   SQL (works anywhere):
#   SELECT id, worker, state, attempt, max_attempts, errors
#   FROM oban_jobs WHERE state IN ('retryable','discarded') ORDER BY attempted_at DESC LIMIT 20;
#
#   IEx (if available):
#   import Ecto.Query
#   MyApp.Repo.all(from j in Oban.Job,
#     where: j.state in ["discarded","retryable"],
#     order_by: [desc: j.attempted_at], limit: 10)

# 5. For LiveView — errors appear in server logs, NOT in the browser console
# Always check the mix phx.server terminal, not browser DevTools
```

**Quick-check before any Prove** (the Elixir equivalent of "is it plugged in"):
```
□ mix compile --warnings-as-errors  — warnings often indicate the actual bug
□ Check mix phx.server output for "GenServer terminating" lines
□ Check changeset.errors before blaming UI or JS
□ Confirm atom vs string keys: IO.inspect(params) in the failing function
□ Confirm the correct function clause is being called: IO.puts("HERE") at entry
```

---

## CATEGORY 1 — ELIXIR PROCESS & OTP

The BEAM's process model — lightweight isolation, message passing, supervisor-led
fault recovery — is the source of bugs that cannot exist in Java or PHP.
Every process has its own heap, mailbox, and stack. Message passing is the only
way processes communicate. A GenServer serialises all access through a single
mailbox. These properties create distinct failure signatures.

### Pattern: GenServer deadlock — `GenServer.call` blocks forever, process never responds
**Symptom:** A request hangs indefinitely. `GenServer.call` never returns. After 5 seconds, `** (exit) exited in: GenServer.call(MyApp.Server, :action, 5000)` — call timeout. The GenServer process is alive (supervisor did not restart it) but completely unresponsive. Restarting the server fixes it temporarily.
**Why:** `GenServer.call/3` sends a message and blocks the caller until the GenServer sends a reply. If the `handle_call/3` implementation calls back into the same GenServer — directly or indirectly through a helper function — the second call waits for the first to complete, which is waiting for the second. The mailbox is blocked. Nothing moves.
**Prove:**
```elixir
# In IEx connected to the running node (iex --sname debug --remsh app@host)
# Or in iex -S mix phx.server during development:

pid = Process.whereis(MyApp.Server)  # or GenServer.whereis(MyApp.Server)

# This call sends a sys message to the GenServer's mailbox.
# If the GenServer is deadlocked — mailbox blocked processing your call —
# :sys.get_state will also block. HANGS = deadlock confirmed.
# Responds instantly = not a deadlock, different problem.
Task.async(fn -> :sys.get_state(pid) end) |> Task.yield(2_000)
# {:ok, state} within 2s → alive, not deadlocked
# nil after 2s → DEADLOCKED — mailbox is blocked

# Also check mailbox queue length
Process.info(pid, :message_queue_len)
# {:message_queue_len, N} where N > 10 and growing = backed up
```
If `:sys.get_state` times out → deadlock confirmed. This is pathognomonic — no other condition causes a GenServer's sys channel to block.
**Fix:** Never call a `GenServer.call` from inside a `handle_call/3` on the same process. Break the circular dependency:
```elixir
# WRONG — circular: handle_call calls back into the same server
def handle_call(:do_work, _from, state) do
  result = MyApp.Server.get_value()  # → GenServer.call(self(), :get_value) → DEADLOCK
  {:reply, result, state}
end

# CORRECT option 1 — use cast for fire-and-forget
def handle_call(:do_work, _from, state) do
  GenServer.cast(self(), :internal_action)  # async, no reply needed from handle_call
  {:reply, :ok, state}
end

# CORRECT option 2 — extract logic to a plain module function
def handle_call(:do_work, _from, state) do
  result = MyApp.Logic.compute(state)  # pure function, no GenServer call
  {:reply, result, state}
end
```
**Dead giveaway:** `GenServer.call(MyApp.Server, ...)` anywhere inside a `handle_call/3` or `handle_info/2` on the same module.

---

### Pattern: GenServer process state contamination — users see each other's data under concurrency
**Symptom:** Under concurrent load, User A sees data belonging to User B. Requests that work correctly in isolation produce wrong results when multiple requests fire simultaneously. Never reproduces in single-user testing. Gets worse with traffic.
**Why:** A GenServer serialises all access — one message processed at a time — which prevents race conditions on its own state. But the state itself is a map or struct, and if request-specific data (current user, current tenant, request parameters) is stored in the GenServer's state between calls, it bleeds from one request into the next. The GenServer is not the problem; the developer used it as a per-request container instead of routing state through function arguments.
**Prove:**
```elixir
# Temporarily log the GenServer state at the START of each handle_call,
# tagging with the caller's identity from the message:
def handle_call({:process, user_id, data}, _from, state) do
  IO.inspect(state.current_user, label: "[CONTAMINATION-PROVE] state.current_user at entry for user_id=#{user_id}")
  # If state.current_user != user_id at the START of this call
  # → previous request's state is still in there → contamination confirmed
  ...
end

# Under concurrent load (run two requests simultaneously):
# Log shows handle_call for user 42 but state.current_user = 7
# = state from user 7's previous request was never cleared
```
If the log shows `state.current_user` differs from the `user_id` in the incoming message at the start of a call → contamination confirmed.
**Fix:** Request-scoped data must flow through function arguments, not GenServer state:
```elixir
# WRONG — storing request context in GenServer state
def handle_call({:process, user_id}, _from, state) do
  state = Map.put(state, :current_user, user_id)  # stays in state for next request!
  result = do_work(state)
  {:reply, result, state}
end

# CORRECT — pass request context as function argument, keep state clean
def handle_call({:process, user_id}, _from, state) do
  result = do_work(user_id, state)  # user_id scoped to this call only
  {:reply, result, state}           # state unchanged, no contamination
end
```

---

### Pattern: Stale PID after supervisor restart — intermittent `noproc` on calls to live process
**Symptom:** Intermittent `** (EXIT) no process: the process is not alive`. The GenServer is running (supervisor shows it healthy, no restart storm). But some callers get `noproc` on random requests. The error is intermittent — most calls succeed, occasional calls fail.
**Why:** A caller resolved the GenServer's PID at startup (via `Process.whereis/1` or `GenServer.whereis/1`) and cached it. The GenServer later crashed and was restarted by the supervisor. The new process has a new PID. The cached PID points to the dead process. `Process.alive?(old_pid)` returns `false`. The caller holds a stale reference and does not know it.
**Prove:**
```elixir
# Find where the PID is being stored in the calling code:
# Look for Process.whereis, GenServer.whereis, or pid(...) stored in state/module attribute

# Then at the call site, add:
cached_pid = state.server_pid  # or wherever it is stored
IO.inspect(Process.alive?(cached_pid), label: "[STALE-PID-PROVE] cached pid alive?")
IO.inspect(Process.whereis(MyApp.Server), label: "[STALE-PID-PROVE] current pid from registry")
# alive?=false AND current pid differs from cached_pid → stale PID confirmed
```
`Process.alive?(cached_pid)` returning `false` is pathognomonic — the cached PID is dead and a new process is running.
**Fix:** Never cache PIDs. Always resolve via the registered name at call time:
```elixir
# WRONG — cached PID goes stale after restart
defmodule MyApp.Client do
  def start_link(_) do
    pid = Process.whereis(MyApp.Server)  # captured once at startup
    {:ok, %{server_pid: pid}}
  end
  def do_work(state) do
    GenServer.call(state.server_pid, :work)  # dead after restart
  end
end

# CORRECT — resolve via name at every call
defmodule MyApp.Client do
  def do_work(_state) do
    GenServer.call(MyApp.Server, :work)  # name resolved fresh each time
    # Or: GenServer.call({:via, Registry, {MyApp.Registry, "key"}}, :work)
  end
end
```
**Dead giveaway:** `state.some_pid` or a module attribute `@server_pid` populated at `start_link` time.

---

### Pattern: `with/1` chain silently returns wrong value — no error, no crash, no log
**Symptom:** A multi-step operation appears to succeed (no error, no exception, no log entry). But the expected side effect never happened — the DB was not written, the email was not sent, the API was not called. The function returns without doing the work. Developers have checked each step individually and they work in isolation.
**Why:** A `with` chain without an `else` clause returns the first non-matching value as-is. If any `<-` step returns something that does not match its left-hand pattern, `with` exits immediately and returns that value to the caller. No exception. No log. The caller, if it also does not pattern-match the return value correctly, silently ignores it.
**Prove:**
```elixir
# Add IO.inspect after EACH <- step to find which one returns unexpectedly:
with {:ok, user}  <- fetch_user(id)   |> IO.inspect(label: "[WITH-PROVE] step1"),
     {:ok, order} <- fetch_order(user) |> IO.inspect(label: "[WITH-PROVE] step2"),
     {:ok, _sent} <- send_email(user, order) |> IO.inspect(label: "[WITH-PROVE] step3") do
  {:ok, :done}
end

# Look for the last step that printed a value.
# The step AFTER the last print = the one that returned unexpectedly and short-circuited.
# e.g. if step1 and step2 print but step3 never prints:
#   → send_email returned something other than {:ok, _}
#   → with exited at step3 silently
```
The last `IO.inspect` that printed is the last step that ran. The missing `IO.inspect` marks the short-circuit point.
**Fix:** Always add an `else` clause to handle non-matching returns:
```elixir
# WRONG — silent exit on any non-matching step
with {:ok, user}  <- fetch_user(id),
     {:ok, order} <- fetch_order(user),
     {:ok, _}     <- send_email(user, order) do
  {:ok, :done}
end  # returns {:error, :not_found} silently if fetch_user fails

# CORRECT — explicit else handles all non-matching cases
with {:ok, user}  <- fetch_user(id),
     {:ok, order} <- fetch_order(user),
     {:ok, _}     <- send_email(user, order) do
  {:ok, :done}
else
  {:error, :not_found}   -> {:error, :user_not_found}
  {:error, :no_orders}   -> {:error, :no_orders_for_user}
  {:error, reason}        -> {:error, reason}
  unexpected              -> {:error, {:unexpected_return, unexpected}}
end
```

---

## CATEGORY 2 — PHOENIX LIVEVIEW

LiveView mounts twice for every page load — once via HTTP (disconnected) and once
via WebSocket (connected). State is per-socket, not per-request. These properties
create failure modes that have no equivalent in controller-based applications.

### Pattern: LiveView silent form save — form submits, nothing happens, no error shown
**Symptom:** User fills in a form and clicks Submit. The page flickers briefly (or does nothing). No error message. No success message. The record is not saved. The browser does not navigate away. Developer has checked the JS event listener, the form action, the button handler — all appear correct.
**Why:** `handle_event/3` received the form submission and called the context function. The context function returned `{:error, changeset}`. The `handle_event` implementation did not handle the error branch — it pattern-matched only `{:ok, _}` and used an unhandled `{:error, changeset}` falling through to a catch-all that returns `{:noreply, socket}` without updating the form with the errors. The user sees the original empty form again. The changeset errors exist but are never assigned to the socket.
**Prove:**
```elixir
# In handle_event where the save happens, add:
def handle_event("save", params, socket) do
  case MyApp.Accounts.create_user(params) do
    {:ok, user} ->
      {:noreply, push_navigate(socket, to: ~p"/users/#{user}")}
    {:error, changeset} ->
      IO.inspect(changeset.errors, label: "[SILENT-SAVE-PROVE] changeset errors")
      # If errors are non-empty → changeset validation failed, errors not surfaced
      {:noreply, assign(socket, :form, to_form(changeset))}
  end
end
# Output shows errors like: [email: {"has already been taken", [...]}]
# User sees blank form = errors present but not being assigned to socket
```
`changeset.errors` being non-empty while the user sees no error message is pathognomonic. The Prove output and the user experience contradict each other — that contradiction IS the bug.
**Fix:** Always handle `{:error, changeset}` and assign the changeset to the socket:
```elixir
# WRONG — only handles success, drops error silently
def handle_event("save", params, socket) do
  {:ok, _user} = MyApp.Accounts.create_user(params)  # crashes on error, doesn't surface it
  {:noreply, push_navigate(socket, to: ~p"/users")}
end

# CORRECT — error branch assigns changeset back to socket for display
def handle_event("save", params, socket) do
  case MyApp.Accounts.create_user(params) do
    {:ok, _user} ->
      {:noreply, push_navigate(socket, to: ~p"/users")}
    {:error, %Ecto.Changeset{} = changeset} ->
      {:noreply, assign(socket, :form, to_form(changeset))}
  end
end
```
**Dead giveaway:** `{:ok, _} = Context.create_something(params)` in a `handle_event/3` — this crashes on error (which surfaces in logs) or is a pin operator against a literal that silently mismatches.

---

### Pattern: LiveView double mount — DB query or side effect executes twice per page load
**Symptom:** The database shows a record created or updated twice for one user action. An email is sent twice. An API is called twice. A counter is incremented by 2 instead of 1. The bug only occurs when the LiveView is first loaded, not on subsequent interactions.
**Why:** LiveView calls `mount/3` twice for every initial page load. The first mount is over HTTP — the server renders the initial HTML. The second mount is over WebSocket — the client connects and mounts again. Any side-effectful code in `mount/3` without a `connected?(socket)` guard runs twice. Database writes, API calls, and email sends all execute on both mounts.
**Prove:**
```elixir
# Add IO.puts at the very top of mount/3:
def mount(_params, _session, socket) do
  IO.puts("[DOUBLE-MOUNT-PROVE] mount called, connected=#{connected?(socket)}")
  # ...
end

# Load the page once in a browser. Watch mix phx.server output.
# You will see TWO lines printed for one page load:
#   [DOUBLE-MOUNT-PROVE] mount called, connected=false   ← HTTP mount
#   [DOUBLE-MOUNT-PROVE] mount called, connected=true    ← WebSocket mount
# Two lines = mount running twice = any side effect in mount runs twice.
```
Seeing two `mount called` lines for one page load is pathognomonic — there is no other explanation.
**Fix:** Guard all side effects with `connected?(socket)`:
```elixir
# WRONG — runs on both HTTP and WebSocket mount
def mount(_params, _session, socket) do
  Audit.log_visit(socket.assigns.current_user)  # logged twice per page load
  {:ok, assign(socket, :data, fetch_data())}
end

# CORRECT — side effects only on connected (WebSocket) mount
def mount(_params, _session, socket) do
  if connected?(socket) do
    Audit.log_visit(socket.assigns.current_user)  # logged once
    Phoenix.PubSub.subscribe(MyApp.PubSub, "updates")
  end
  {:ok, assign(socket, :data, fetch_data())}  # read-only fetch is fine on both
end
```

---

### Pattern: LiveView PubSub duplicate messages — every broadcast received twice by the same LiveView
**Symptom:** Every real-time update appears twice in the UI. When someone posts a message, it appears twice in the chat. When a record updates, two identical `handle_info` callbacks fire. The duplication is consistent — always exactly 2×, never 3× or intermittent.
**Why:** `Phoenix.PubSub.subscribe/2` is called in `mount/3` without a `connected?(socket)` guard. Since `mount/3` runs twice (HTTP + WebSocket), the same LiveView process subscribes to the same topic twice. Every subsequent broadcast is delivered twice to that process, triggering two `handle_info` callbacks.
**Prove:** Add a counter to `handle_info/2` to detect how many times a single broadcast arrives:
```elixir
# Step 1 — add a process-level counter at the top of your LiveView module:
def mount(_params, _session, socket) do
  Process.put(:pubsub_receive_count, 0)  # reset counter on each mount
  Phoenix.PubSub.subscribe(MyApp.PubSub, "updates:#{room_id}")  # current code unchanged
  {:ok, socket}
end

# Step 2 — count every handle_info invocation for the broadcast message:
def handle_info({:new_message, msg}, socket) do
  count = Process.get(:pubsub_receive_count, 0) + 1
  Process.put(:pubsub_receive_count, count)
  IO.puts("[PUBSUB-PROVE] handle_info call ##{count} for pid=#{inspect(self())}")
  # Broadcast ONE message via Phoenix.PubSub.broadcast(MyApp.PubSub, "updates:...", {:new_message, %{}})
  # Expected: "[PUBSUB-PROVE] handle_info call #1 ..." printed once
  # Bug:      "[PUBSUB-PROVE] handle_info call #1 ..." AND "#2 ..." for one broadcast → subscribed twice
  {:noreply, socket}
end
```
Two `handle_info` calls for a single `broadcast` is pathognomonic — the same process holds two subscriptions to the same topic, so each broadcast is delivered twice.
**Fix:** Always guard PubSub subscriptions with `connected?(socket)`:
```elixir
# WRONG — subscribes on HTTP mount AND WebSocket mount = 2 subscriptions
def mount(_params, _session, socket) do
  Phoenix.PubSub.subscribe(MyApp.PubSub, "updates:#{room_id}")
  {:ok, socket}
end

# CORRECT — subscribes only on WebSocket mount = 1 subscription
def mount(_params, _session, socket) do
  if connected?(socket) do
    Phoenix.PubSub.subscribe(MyApp.PubSub, "updates:#{room_id}")
  end
  {:ok, socket}
end
```

---

### Pattern: LiveView `assign_async` stale closure — async result always shows initial or stale value
**Symptom:** `assign_async` is used to load data asynchronously. The data loads but always shows an old value — a user ID, permission scope, or tenant that belonged to the previous navigation state. The async task itself runs (the `{:ok, %{...}}` is returned). But the fetched data is for the wrong context. Navigating to a different record or user shows stale data from the previous one.
**Why:** Elixir closures capture the value of **variables** at the moment the closure is defined — not the value of `socket.assigns` at execution time. The bug occurs in `handle_params/3`: when the user navigates to a new record, `handle_params` is called with new params and triggers `assign_async`. But if the closure references `socket.assigns.current_scope` directly instead of an extracted local variable, the closure captures the socket from `handle_params`'s parameter — which may be the *old* socket before the new assigns were applied. The async task then fetches data for the old scope.
**Prove:** Add inspection inside the `assign_async` closure in `handle_params/3` to compare captured vs expected values:
```elixir
def handle_params(%{"id" => id}, _uri, socket) do
  # Extract BEFORE any socket update — this is what the closure will capture
  old_scope_id = socket.assigns.scope.id
  IO.inspect(old_scope_id, label: "[ASYNC-CLOSURE-PROVE] scope.id at closure definition")

  # Update socket with new scope
  socket = assign(socket, :scope, MyApp.get_scope(id))

  {:noreply,
   assign_async(socket, :data, fn ->
     # This runs asynchronously — what scope.id does it use?
     IO.inspect(old_scope_id, label: "[ASYNC-CLOSURE-PROVE] scope.id INSIDE closure")
     # If old_scope_id ≠ id (the new param) → closure is fetching for the WRONG scope
     {:ok, %{data: MyApp.fetch(old_scope_id)}}
   end)}
end
# Trigger by navigating: /items/1 then /items/2 quickly
# If "[INSIDE closure] scope.id = 1" when you navigated to /items/2 → stale capture confirmed
```
`old_scope_id` inside the closure differing from the current navigation target is pathognomonic.
**Fix:** Extract the value you need *after* the socket update, then pass it into the closure:
```elixir
# WRONG — closure captures socket from handle_params param (may be pre-update socket)
def handle_params(%{"id" => id}, _uri, socket) do
  socket = assign(socket, :scope, MyApp.get_scope(id))
  {:noreply,
   assign_async(socket, :data, fn ->
     {:ok, %{data: MyApp.fetch(socket.assigns.scope.id)}}  # captures old socket, not updated one
   end)}
end

# CORRECT — extract from the UPDATED socket, then close over the local variable
def handle_params(%{"id" => id}, _uri, socket) do
  socket = assign(socket, :scope, MyApp.get_scope(id))
  scope_id = socket.assigns.scope.id  # extracted from UPDATED socket
  {:noreply,
   assign_async(socket, :data, fn ->
     {:ok, %{data: MyApp.fetch(scope_id)}}  # local variable — correct value
   end)}
end
```

---

### Pattern: LiveView embedded schema — `hidden_input` missing, embedded fields silently dropped
**Symptom:** A form that includes embedded schema fields (using `embeds_one` or `embeds_many`) saves successfully — no error, no validation failure — but the embedded fields are always empty or nil in the database. The parent record saves; the embedded struct fields do not. Inspecting the changeset shows the embedded struct is empty.
**Why:** Phoenix LiveView forms require a `hidden_input` for every required field in an embedded schema that is not directly editable by the user. Without `hidden_input`, the form submission does not include that field in the params. `cast_embed/3` in the changeset receives no data for that field and leaves it empty. The changeset is valid (missing embedded fields may not trigger validation), so the save appears to succeed.
**Prove:**
```elixir
# In handle_event("save", params, socket):
def handle_event("save", params, socket) do
  IO.inspect(params, label: "[HIDDEN-INPUT-PROVE] raw params received")
  # Look for the embedded schema key (e.g. "profile", "address")
  # If params["user"]["profile"] is %{} or missing → hidden_input not sending the data

  changeset = User.changeset(%User{}, params["user"])
  IO.inspect(changeset.changes, label: "[HIDDEN-INPUT-PROVE] changeset.changes")
  # If changeset.changes[:profile] is %{} or not present → embedded fields not received
  ...
end
```
`params` showing empty map `%{}` for the embedded key confirms the form is not sending the embedded field data — `hidden_input` is missing.
**Fix:** Add `hidden_input` for every required field in an embedded schema that is not directly shown in the form:
```elixir
# WRONG — embedded schema has required :type field but no hidden_input
<.form for={@form} phx-submit="save">
  <.input field={@form[:name]} label="Name" />
  <%# @form[:profile][:type] required but no hidden_input — silently dropped %>
</.form>

# CORRECT — hidden_input ensures :type is submitted even when not shown to user
<.form for={@form} phx-submit="save">
  <.input field={@form[:name]} label="Name" />
  <.inputs_for :let={profile_form} field={@form[:profile]}>
    <.input type="hidden" field={profile_form[:type]} />
    <%# visible fields here %>
  </.inputs_for>
</.form>
```
**Dead giveaway:** `embeds_one` or `embeds_many` in the schema, combined with a form that uses `inputs_for`, and the embedded fields showing as empty after a successful save.

---

## CATEGORY 3 — ECTO & DATABASE

### Pattern: Ecto N+1 — association access in loop fires one query per record, fast in dev, timeout in prod
**Symptom:** A page or API endpoint loads in under 100ms with 10 records. With 500 records (production volume), it times out or takes 30+ seconds. The DB server shows high query count, not slow individual queries. No code change between environments — only data volume differs.
**Why:** Accessing an association in a loop without preloading it fires one SQL query per record. `Enum.map(users, fn u -> u.posts end)` where posts are not preloaded executes `SELECT * FROM posts WHERE user_id = $1` once per user. 500 users = 501 queries (1 for users + 500 for posts). Each query is fast; 500 sequential queries are slow.
**Prove:**
```elixir
# Option A — telemetry attach (dev/staging only — requires running IEx session):
# ⚠️ Dev/staging only. Production requires iex --remsh or code deploy.
:telemetry.attach(
  "n1-prove",
  [:my_app, :repo, :query],  # replace :my_app with your app name
  fn _event, _measurements, metadata, _config ->
    IO.puts("[N1-PROVE] query: #{String.slice(metadata.query, 0, 80)}")
  end,
  nil
)
# Trigger the slow operation. Count the query lines.
# If count equals (record_count + 1) → N+1 confirmed.
# Detach when done: :telemetry.detach("n1-prove")

# Option B — DB slow query log (production-safe, no code change):
# In config/dev.exs or config/prod.exs:
config :my_app, MyApp.Repo,
  log: :debug,        # logs all queries
  stacktrace: true    # shows which line triggered the query
# Then trigger the operation and count identical queries in the log.
# grep "SELECT.*FROM posts WHERE user_id" dev.log | wc -l
# N lines for N users = N+1 confirmed

# Option C — inline counter (any environment, no IEx required):
query_count = :counters.new(1, [])
:telemetry.attach("n1-count", [:my_app, :repo, :query],
  fn _, _, _, _ -> :counters.add(query_count, 1, 1) end, nil)
result = MyApp.list_users_with_posts()  # trigger the operation
:telemetry.detach("n1-count")
IO.puts("[N1-PROVE] total queries: #{:counters.get(query_count, 1)}")
```
Query count matching record count is pathognomonic.
**Fix:** Preload associations before the loop:
```elixir
# WRONG — triggers 1 query per user inside the loop
users = Repo.all(User)
Enum.map(users, fn user ->
  {user.name, user.posts}  # triggers SELECT posts WHERE user_id = ? per user
end)

# CORRECT — 2 queries total regardless of record count
users = Repo.all(User) |> Repo.preload(:posts)
Enum.map(users, fn user ->
  {user.name, user.posts}  # already loaded, no query
end)

# For nested associations:
users = Repo.all(User) |> Repo.preload(posts: :comments)
```

---

### Pattern: Ecto.Multi transaction rollback invisible — step fails, data silently not saved
**Symptom:** An `Ecto.Multi` pipeline appears to execute successfully — no exception is raised. But the expected database records are not created. Related records are missing. The operation returns without error. Developer has verified each individual step works in isolation.
**Why:** `Repo.transaction(multi)` returns `{:ok, results}` or `{:error, step_name, changeset, completed_changes}`. If the caller pattern-matches only `{:ok, results}` (or uses `{:ok, _} = Repo.transaction(multi)`), a failing step returns `{:error, step_name, changeset, _}` which does not match `{:ok, _}`, causing a `MatchError` — or, if no match is attempted, the error tuple is silently ignored. The transaction rolls back all completed steps; none of the changes persist.
**Prove:**
```elixir
# Run the Multi and inspect the raw return value:
result = Repo.transaction(multi)
IO.inspect(result, label: "[MULTI-PROVE] transaction result")

# {:ok, %{user: user, profile: profile}} → all steps succeeded
# {:error, :profile, %Ecto.Changeset{}, %{user: user}} →
#   :profile step failed, user was rolled back too
#   changeset.errors shows WHY :profile failed

# To find which step is failing:
result
|> case do
  {:ok, changes} ->
    IO.inspect(Map.keys(changes), label: "[MULTI-PROVE] completed steps")
  {:error, failed_step, failed_value, completed} ->
    IO.inspect(failed_step, label: "[MULTI-PROVE] FAILED STEP")
    IO.inspect(failed_value, label: "[MULTI-PROVE] failure reason/changeset")
    IO.inspect(Map.keys(completed), label: "[MULTI-PROVE] steps that ran before failure")
end
```
`{:error, :step_name, changeset, _}` in the output identifies exactly which step failed and why.
**Fix:** Always pattern-match both the success and failure cases of `Repo.transaction`:
```elixir
# WRONG — crashes on error with MatchError, or silently ignores {:error, ...}
{:ok, %{user: user}} = Repo.transaction(multi)

# CORRECT — handle both cases explicitly
case Repo.transaction(multi) do
  {:ok, %{user: user, profile: profile}} ->
    {:ok, user}
  {:error, :user, changeset, _changes} ->
    {:error, {:user_creation_failed, changeset}}
  {:error, :profile, changeset, _changes} ->
    {:error, {:profile_creation_failed, changeset}}
  {:error, failed_operation, failed_value, _changes} ->
    {:error, {failed_operation, failed_value}}
end
```

---

### Pattern: Ecto unique constraint race — validation passes, DB constraint violation in production under load
**Symptom:** `Repo.insert(changeset)` raises `Ecto.ConstraintError` or returns `{:error, changeset}` with a `unique_constraint` error. But the changeset validation passed — `changeset.valid?` was `true`. The error only occurs under concurrent load, not in single-user testing. A `unique_index` exists on the column.
**Why:** The validation check (a custom `Repo.exists?` or `Repo.get_by` call before insert) runs a `SELECT` to see if the value exists. If two concurrent requests both pass the `SELECT` check at the same time (the value does not exist yet for either), both proceed to `INSERT`. The second `INSERT` hits the database-level unique constraint. The validation caught nothing because the race window is between the check and the insert.
**Prove:**
```elixir
# Reproduce with concurrent requests (use Task.async_stream or ab/wrk):
params = %{email: "test@example.com", name: "Test User"}
tasks = for _ <- 1..5, do: Task.async(fn -> MyApp.Accounts.create_user(params) end)
results = Task.await_many(tasks)
IO.inspect(results, label: "[CONSTRAINT-RACE-PROVE] concurrent insert results")
# Expected for correct code: {:ok, user} once, {:error, changeset} four times
# If you see Ecto.ConstraintError raised → unique_constraint not handled in changeset
# If you see multiple {:ok, user} → constraint not enforced at DB level

# Check whether the constraint is handled in the changeset:
changeset = User.changeset(%User{}, params)
IO.inspect(changeset.constraints, label: "[CONSTRAINT-RACE-PROVE] constraints registered")
# Should show: [%{type: :unique, constraint: "users_email_index", field: :email, ...}]
# Empty list → unique_constraint not added to changeset → error will raise instead of return {:error}
```
Multiple `{:ok, user}` results from concurrent inserts = constraint not enforced at DB level. `Ecto.ConstraintError` raised = constraint not handled in changeset.
**Fix:** Add the constraint to the changeset AND use database-level uniqueness:
```elixir
# 1. Database migration — the only true race-safe guarantee:
create unique_index(:users, [:email])

# 2. Changeset — handle the constraint as a user-friendly error:
def changeset(user, attrs) do
  user
  |> cast(attrs, [:email, :name])
  |> validate_required([:email])
  |> validate_format(:email, ~r/@/)
  |> unique_constraint(:email)  # converts ConstraintError to {:error, changeset}
  # Do NOT do a manual Repo.exists?/Repo.get_by check before Repo.insert —
  # that SELECT-then-INSERT pattern has a race window between the two operations
end

# 3. Caller handles the error cleanly:
case Repo.insert(changeset) do
  {:ok, user} -> {:ok, user}
  {:error, %{errors: [email: {"has already been taken", _}]}} -> {:error, :email_taken}
  {:error, changeset} -> {:error, changeset}
end
```

---

## CATEGORY 4 — OBAN / BACKGROUND JOBS

### Pattern: Oban struct-in-args — `perform/1` pattern match fails, struct fields are null in DB
**Symptom:** An Oban job is inserted and runs (the `perform/1` function executes). But the business logic never takes effect — the expected DB writes, API calls, or emails do not happen. No error in the failed_jobs table. No exception in the logs. The job state is `completed`. Adding IO.inspect at the top of `perform/1` shows the args are partially or fully empty.
**Why:** Oban stores job args as JSON in the `oban_jobs` table. Elixir structs (like `%User{}`, `%Order{}`, `%MyApp.SomeStruct{}`) do not serialize to JSON correctly — they lose their struct type and their fields become an empty map `{}`. The `perform/1` function pattern-matches on the struct fields (e.g. `%{"user_id" => id}`) but the args contain only `{}`. The pattern match for the specific key fails, execution falls through to a catch-all that returns `:ok`, and the job completes as if it succeeded.

A subtle variant: the developer uses atom keys (`%{user_id: id}`) in the job args. JSON serialization converts atom keys to string keys. The `perform/1` function pattern-matches on atom keys and silently fails to match, returning a wrong value.
**Prove:**
```elixir
# Inspect the actual args stored in the DB for a recent job:
# (Run this in IEx or as a one-off mix task)
import Ecto.Query
job = MyApp.Repo.one(
  from j in Oban.Job,
  where: j.worker == "MyApp.Workers.EmailWorker",
  order_by: [desc: j.inserted_at],
  limit: 1
)
IO.inspect(job.args, label: "[OBAN-ARGS-PROVE] args stored in DB")
# Expected: %{"user_id" => 42, "order_id" => 7}
# Bug: %{} → struct was serialized as empty map
# Bug: %{"user" => %{}} → struct nested inside args → also empty

# Also check: are you pattern matching atom keys or string keys?
# Atom keys in Elixir: %{user_id: id}
# String keys from JSON: %{"user_id" => id}
# perform/1 receives STRING keys. Atom key match = always fails.
```
`job.args` showing `%{}` when the job was inserted with a struct confirms struct serialization. `job.args` showing string keys when `perform/1` pattern-matches atom keys confirms the key type mismatch.
**Fix:** Store only IDs and plain values in args. Never store structs. Always pattern-match string keys in `perform/1`:
```elixir
# WRONG — struct in args serializes to empty map
Oban.insert(MyApp.Workers.EmailWorker.new(%{user: %User{id: 42, email: "a@b.com"}}))
# → args in DB: %{"user" => %{}}  → pattern match fails

# WRONG — atom keys in args become string keys after JSON round-trip
Oban.insert(MyApp.Workers.EmailWorker.new(%{user_id: 42}))
# args stored in DB: %{"user_id" => 42}  (string keys — JSON conversion)
def perform(%Oban.Job{args: %{user_id: id}}) do  # atom key pattern — NEVER matches string key
  send_email(id)  # this line never executes
end

# CORRECT — plain values, string key pattern match
Oban.insert(MyApp.Workers.EmailWorker.new(%{user_id: 42, order_id: 7}))
def perform(%Oban.Job{args: %{"user_id" => user_id, "order_id" => order_id}}) do
  user = MyApp.Repo.get!(User, user_id)
  order = MyApp.Repo.get!(Order, order_id)
  MyApp.Mailer.send_confirmation(user, order)
end
```

---

### Pattern: Oban job marked `completed` but business logic never ran — wrong return value
**Symptom:** Oban jobs run on schedule (the queue is active, the worker is executing). But the expected effect never happens — records not created, emails not sent, APIs not called. The `oban_jobs` table shows `state = 'completed'`. No entries in `failed_jobs`. Inserting a new job with the same args produces the same result.
**Why:** Oban marks a job `completed` when `perform/1` returns `:ok` or `{:ok, _}`. If `perform/1` contains a bug that causes it to return early — before executing the business logic — Oban has no way to know the job "failed" from a business perspective. Common causes: a `with` chain that short-circuits (see Category 1, Pattern 4) and returns `{:error, reason}` from an inner step, but the `perform/1` caller doesn't check the return and returns `:ok` anyway. Or a pattern match on the result of the context function that silently mismatches.
**Prove:**
```elixir
# Add IO.inspect at every exit point in perform/1:
def perform(%Oban.Job{args: %{"user_id" => user_id}}) do
  IO.puts("[OBAN-RETURN-PROVE] perform/1 started for user_id=#{user_id}")

  result = with {:ok, user}  <- MyApp.Accounts.get_user(user_id),
                {:ok, order} <- MyApp.Orders.get_latest(user),
                {:ok, _sent} <- MyApp.Mailer.send(user, order) do
    IO.puts("[OBAN-RETURN-PROVE] all steps succeeded")
    :ok
  end

  IO.inspect(result, label: "[OBAN-RETURN-PROVE] perform/1 final return value")
  result
end
# If result is {:error, :not_found} or similar non-:ok value,
# and the caller returns :ok regardless → job marked complete incorrectly.
# The with chain is returning an error but perform/1 returns :ok.
```
`result` being `{:error, _}` while the job shows `completed` confirms the return value is not being propagated correctly.
**Fix:** Ensure `perform/1` returns the correct value for each outcome:
```elixir
# WRONG — ignores error from with chain, always returns :ok
def perform(%Oban.Job{args: %{"user_id" => user_id}}) do
  with {:ok, user} <- get_user(user_id),
       {:ok, _}    <- send_email(user) do
    :ok
  end
  :ok  # ← this :ok executes even if with chain returns {:error, _}
end

# CORRECT — propagate the return value; Oban handles each case
def perform(%Oban.Job{args: %{"user_id" => user_id}}) do
  with {:ok, user} <- get_user(user_id),
       {:ok, _}    <- send_email(user) do
    :ok                          # success → Oban marks completed
  else
    {:error, :not_found} ->
      {:cancel, "user not found"}  # permanent failure → Oban marks cancelled
    {:error, :rate_limited} ->
      {:snooze, 300}               # retry in 5 minutes → Oban marks snoozed
    {:error, reason} ->
      {:error, reason}             # transient failure → Oban marks retryable
  end
end
```

---

## CATEGORY 5 — PHOENIX FRAMEWORK

### Pattern: Phoenix Plug pipeline auth bypass — protected route accessible without authentication
**Symptom:** A route that should require authentication is accessible without logging in. The authentication plug exists and works on other routes. Adding the authentication check directly in the controller action works. Removing it breaks things. But the route remains accessible without authentication even with the plug defined.
**Why:** Phoenix applies plugs in pipeline order. A route is protected only if it is inside a `pipe_through` scope that includes the authentication plug. Routes defined outside that scope, or inside a scope with a different pipeline, bypass the plug entirely. The plug is registered — it just is not applied to that specific route.
**Prove:** Two steps — confirm the route exists, then find which pipeline scope owns it:
```bash
# Step 1 — confirm the route is registered at all:
mix phx.routes | grep "reports"
# Output: GET  /admin/reports  MyAppWeb.ReportController  :index
# (mix phx.routes shows: verb, path, controller, action — no pipeline column)
# Route exists → the issue is which pipeline applies, not whether the route is defined.

# Step 2 — find the scope that owns this route in router.ex:
grep -n "reports\|pipe_through\|scope" lib/my_app_web/router.ex
# Look for the scope block that contains "get "/reports""
# If that scope's pipe_through list does NOT include your auth plug → bug confirmed
```
Finding the route inside a `scope` block whose `pipe_through` omits the auth plug is pathognomonic — the plug is never invoked for that route regardless of what is in the controller.
**Verify after fix:**
```bash
# After moving the route into the authenticated scope, confirm no 401/redirect is skipped:
curl -I http://localhost:4000/admin/reports
# Expected: HTTP/1.1 302 Found  Location: /login  (redirect to login)
# Bug state was: HTTP/1.1 200 OK  (no redirect)
```
**Fix:** Ensure the protected route is inside a scope that `pipe_through` the authentication plug:
```elixir
# WRONG — /admin/reports is outside the authenticated scope
scope "/admin", MyAppWeb do
  pipe_through [:browser, :require_authenticated_user]
  resources "/users", UserController  # protected
end

scope "/admin", MyAppWeb do
  pipe_through [:browser]             # no auth!
  get "/reports", ReportController, :index  # accessible without auth
end

# CORRECT — all /admin routes inside the authenticated scope
scope "/admin", MyAppWeb do
  pipe_through [:browser, :require_authenticated_user]
  resources "/users", UserController
  get "/reports", ReportController, :index  # now protected
end
```
After the fix: `curl -I http://localhost:4000/admin/reports` should return HTTP 302 (redirect to login), not HTTP 200.
**Dead giveaway:** Two `scope "/admin"` blocks with different `pipe_through` configurations. Routes accidentally placed in the lower-privilege scope.

