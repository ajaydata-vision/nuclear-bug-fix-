# EL-005: LiveView Profile Form Submits But Changes Not Saved

## User Prompt

Our Phoenix LiveView profile page has a form for updating name, bio, and timezone. When users click Save, the page briefly flickers and returns to the form. No success message. No error message. No validation errors shown. The database record is unchanged. We checked the JS console — no errors. The phx-submit event fires correctly.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Phoenix LiveView 0.20.4
- environment: production and local dev (same behaviour)
- logs: no errors in server logs
- code excerpt:
```elixir
defmodule MyAppWeb.ProfileLive do
  use MyAppWeb, :live_view

  def mount(_params, _session, socket) do
    user = socket.assigns.current_user
    changeset = Accounts.change_profile(user)
    {:ok, assign(socket, :form, to_form(changeset))}
  end

  def handle_event("save", params, socket) do
    user = socket.assigns.current_user
    case Accounts.update_profile(user, params["user"]) do
      {:ok, updated_user} ->
        {:noreply, push_navigate(socket, to: ~p"/profile")}
    end
  end
end
```
