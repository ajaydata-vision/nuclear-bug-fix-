# Verification

## After Fix

```elixir
def mount(%{"room_id" => room_id}, _session, socket) do
  if connected?(socket) do
    Phoenix.PubSub.subscribe(MyApp.PubSub, "room:#{room_id}")
  end
  {:ok, assign(socket, :messages, [])}
end
```

## Regression Checks

- Send one message: appears exactly once for all connected users
- User joins room: receives subsequent messages exactly once
- User disconnects and reconnects: one subscription active, no duplicates
