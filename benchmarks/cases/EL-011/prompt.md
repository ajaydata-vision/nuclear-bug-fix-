# EL-011: Account Creation Returns OK But User and Profile Missing From DB

## User Prompt

Our account creation function uses Ecto.Multi to create a user, their profile, and their settings atomically. The function returns `{:ok, account}` with no error. But when we query the database, only the account record exists — the user and profile records are missing. No exception is raised anywhere in the call stack.

## Context Provided To The Skill

- stack: Elixir 1.15, Phoenix 1.7.8, Ecto 3.10.3, PostgreSQL 15
- environment: production (first noticed) and local (reproduced)
- logs: no errors
- code excerpt:
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

  {:ok, "account created"}
end
```
