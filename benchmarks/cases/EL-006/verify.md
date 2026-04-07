# Verification

## After Fix

```elixir
def mount(%{"token" => token}, _session, socket) do
  case Accounts.verify_registration_token(token) do
    {:ok, user} ->
      if connected?(socket), do: Mailer.send_welcome_email(user)
      {:ok, assign(socket, :user, user)}
    {:error, _} ->
      {:ok, redirect(socket, to: ~p"/register")}
  end
end
```

## Regression Checks

- New registration: exactly one welcome email delivered
- Page refresh: no additional email sent (token verification fails on second use)
- Slow connection (WebSocket connects late): still exactly one email
