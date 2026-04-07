# EL-004: User Onboarding Function Returns :ok But Welcome Email Never Arrives

## User Prompt

Our user onboarding function creates the user, sets up their workspace, and sends a welcome email. It returns `:ok` with no error. Users are being created in the database. But welcome emails are never sent — not in spam, not in any email provider logs. No error anywhere. Mailer works fine when tested in isolation.

## Context Provided To The Skill

- stack: Elixir 1.15, Phoenix 1.7, Swoosh mailer
- environment: production and staging (same behaviour)
- logs: no errors related to onboarding
- code excerpt:
```elixir
def onboard_user(attrs) do
  with {:ok, user}      <- Accounts.create_user(attrs),
       {:ok, workspace} <- Workspaces.create_default(user),
       {:ok, _email}    <- Mailer.send_welcome(user) do
    Logger.info("Onboarding complete for #{user.email}")
    :ok
  end
  :ok
end
```
- reproduction:
  1. Call onboard_user with valid attrs
  2. Returns :ok immediately
  3. User and workspace created in DB
  4. No email sent, no log of "Onboarding complete"
  5. `Mailer.send_welcome(user)` works correctly when called directly in IEx
