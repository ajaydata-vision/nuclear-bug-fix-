# Verification

## After Fix

```elixir
def onboard_user(attrs) do
  with {:ok, user}      <- Accounts.create_user(attrs),
       {:ok, workspace} <- Workspaces.create_default(user),
       {:ok, _email}    <- Mailer.send_welcome(user) do
    Logger.info("Onboarding complete for #{user.email}")
    {:ok, user}
  else
    {:error, :email_failed} -> {:error, :welcome_email_failed}
    {:error, reason}        -> {:error, reason}
  end
end
```

## Regression Checks

- Valid attrs: returns `{:ok, user}`, "Onboarding complete" logged, email sent
- Invalid email: returns `{:error, changeset}`, no user/workspace created, no email
- Email misconfigured: returns `{:error, :email_failed}`, user+workspace created (decide on rollback policy)
