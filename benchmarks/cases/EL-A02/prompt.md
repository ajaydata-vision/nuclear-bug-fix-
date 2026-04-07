# EL-A02: Double Mount Bug — Tests Pass, Emails Still Sent Twice in Production

## User Prompt

We identified that our welcome email is being sent twice due to the LiveView double mount issue. We fixed it by adding `if connected?(socket)` guard. We wrote a test for it. The test passes — only one email is sent in the test. But in production, users still receive two welcome emails. We've deployed the fix twice and triple-checked the code. The fix is definitely in production. Why is our test passing but the bug still happening?

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11, Phoenix LiveView 0.20.14
- environment: Fix deployed, tests pass, production still broken
- logs (production):
  - `[info] Sending welcome email (connected=true)` ← correct, guarded
  - `[info] Welcome email delivered`
  - `[info] Sending welcome email` ← second send, NO connected= log
- code excerpt (after fix):
```elixir
def mount(%{"token" => token}, _session, socket) do
  case Accounts.verify_registration_token(token) do
    {:ok, user} ->
      if connected?(socket) do
        Logger.info("Sending welcome email (connected=#{connected?(socket)})")
        Mailer.send_welcome_email(user)
      end
      {:ok, assign(socket, :user, user)}
    {:error, _} ->
      {:ok, redirect(socket, to: ~p"/register")}
  end
end
```

```elixir
# The passing test:
test "sends exactly one welcome email on registration" do
  {:ok, view, _html} = live(conn, ~p"/register/confirm?token=#{token}")
  assert_email_delivered_with(subject: "Welcome!")
  refute_email_delivered_with(subject: "Welcome!")
end
```
