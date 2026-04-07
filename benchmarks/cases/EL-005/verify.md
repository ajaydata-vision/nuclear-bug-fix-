# Verification

## After Fix

```elixir
def handle_event("save", params, socket) do
  user = socket.assigns.current_user
  case Accounts.update_profile(user, params["user"]) do
    {:ok, _updated_user} ->
      {:noreply, push_navigate(socket, to: ~p"/profile")}
    {:error, %Ecto.Changeset{} = changeset} ->
      {:noreply, assign(socket, :form, to_form(changeset))}
  end
end
```

## Regression Checks

- Valid update (name changed): navigates to /profile, DB updated
- Invalid update (blank name): form re-renders with "can't be blank" error shown to user
- DB error: form re-renders with error, no navigation
