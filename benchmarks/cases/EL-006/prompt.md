# EL-006: Welcome Email Sent Twice on Signup

## User Prompt

New users receive two welcome emails every time they sign up. The `send_welcome_email` function is called in our `RegistrationLive` LiveView mount. It works correctly when called from a controller — only one email. We've added logging and confirmed the function is being called twice, but we don't understand why. There's only one `mount/3` function and one call to `send_welcome_email`.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Phoenix LiveView 0.20.14
- environment: production
- logs:
  - `[info] Sending welcome email to new_user@example.com`
  - `[info] Welcome email delivered: new_user@example.com`
  - `[info] Sending welcome email to new_user@example.com`  ← duplicate
  - `[info] Welcome email delivered: new_user@example.com`  ← duplicate
- code excerpt:
```elixir
defmodule MyAppWeb.RegistrationLive do
  use MyAppWeb, :live_view

  def mount(%{"token" => token}, _session, socket) do
    case Accounts.verify_registration_token(token) do
      {:ok, user} ->
        Mailer.send_welcome_email(user)
        {:ok, assign(socket, :user, user)}
      {:error, _} ->
        {:ok, redirect(socket, to: ~p"/register")}
    end
  end
end
```
