# Verification

## After Fix

```elixir
def register_user(attrs) do
  attrs
  |> User.registration_changeset()
  |> Repo.insert()
  # Repo.insert returns {:error, changeset} with email: ["has already been taken"]
  # when unique_constraint(:email) is in the changeset
end

# In User changeset:
def registration_changeset(user \\ %User{}, attrs) do
  user
  |> cast(attrs, [:email, :password])
  |> validate_required([:email, :password])
  |> unique_constraint(:email)  # handles the race at DB level
end
```

## Regression Checks

- 5 concurrent registrations same email: exactly 1 {:ok, user}, 4 {:error, changeset with email taken}
- Sequential registration: works as before
- Ecto.ConstraintError: no longer raised (unique_constraint converts it to {:error, changeset})
