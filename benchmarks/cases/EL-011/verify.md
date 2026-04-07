# Verification

## After Fix

```elixir
def create_full_account(attrs) do
  Multi.new()
  |> Multi.insert(:account, Account.changeset(%Account{}, attrs))
  |> Multi.insert(:user, fn %{account: account} ->
    User.changeset(%User{}, %{account_id: account.id, email: attrs.email})
  end)
  |> Multi.insert(:profile, fn %{user: user} ->
    Profile.changeset(%Profile{}, %{user_id: user.id})
  end)
  |> Repo.transaction()
  |> case do
    {:ok, %{account: account}} -> {:ok, account}
    {:error, :user, changeset, _} -> {:error, {:user_failed, changeset}}
    {:error, :profile, changeset, _} -> {:error, {:profile_failed, changeset}}
    {:error, step, value, _} -> {:error, {step, value}}
  end
end
```

## Regression Checks

- Valid attrs: {:ok, account}, user and profile in DB
- Duplicate email: {:error, {:user_failed, changeset}}, no account/user/profile in DB
- Profile validation failure: {:error, {:profile_failed, changeset}}, no records in DB
