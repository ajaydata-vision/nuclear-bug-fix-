# EL-007: Chat Messages Appear Twice for All Users

## User Prompt

Every message in our Phoenix LiveView chat appears twice in the message list for every connected user. The `handle_info` callback is being called twice for each broadcast. The broadcast itself is called once — we verified with logging. The deduplication logic we added on the client side didn't help because both messages arrive at the server level. Happens for all users simultaneously.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.12, Phoenix LiveView 0.20.14, Phoenix.PubSub 2.1.3
- environment: production and local dev
- logs:
  - `[info] Broadcasting message_id=abc123 to room:42`
  - `[debug] handle_info called for message_id=abc123 on pid=<0.234.0>`
  - `[debug] handle_info called for message_id=abc123 on pid=<0.234.0>` ← same pid, same message
- code excerpt:
```elixir
defmodule MyAppWeb.ChatLive do
  use MyAppWeb, :live_view

  def mount(%{"room_id" => room_id}, _session, socket) do
    Phoenix.PubSub.subscribe(MyApp.PubSub, "room:#{room_id}")
    {:ok, assign(socket, :messages, [])}
  end

  def handle_info({:new_message, message}, socket) do
    Logger.debug("handle_info called for message_id=#{message.id} on pid=#{inspect(self())}")
    {:noreply, update(socket, :messages, &[message | &1])}
  end
end
```
