# EL-012: Duplicate User Accounts Created Despite Email Uniqueness Check

## User Prompt

We're seeing duplicate user accounts with the same email address in production. Our code explicitly checks if the email exists before creating the account. The check returns false, then we create the account — but somehow two users with the same email end up in the database. Has a unique index on email. Never reproduces in sequential testing. Only happens in production during traffic spikes.

## Context Provided To The Skill

- stack: Elixir 1.15, Phoenix 1.7.9, Ecto 3.10, PostgreSQL 15
- environment: production (traffic spikes), not reproducible with sequential requests
- logs:
  - `[info] Email check: user@example.com not found, proceeding with creation`
  - `[info] Email check: user@example.com not found, proceeding with creation` ← concurrent
  - `Ecto.ConstraintError: unique constraint "users_email_index" violated` (occasionally)
- code excerpt:
```elixir
def register_user(attrs) do
  email = attrs["email"]

  if Repo.exists?(from u in User, where: u.email == ^email) do
    {:error, :email_taken}
  else
    user_changeset = User.changeset(%User{}, attrs)
    Repo.insert(user_changeset)
  end
end
```
