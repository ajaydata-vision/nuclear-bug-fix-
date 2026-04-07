# EL-015: Admin Export Endpoint Returns 200 Without Authentication

## User Prompt

Our Phoenix API has an admin export endpoint `/api/admin/export` that should require admin authentication. It returns HTTP 200 and the full data export without any auth token. Other admin endpoints like `/api/admin/users` correctly return 401 when called without auth. The `RequireAdmin` plug exists and works on the other routes. We confirmed the plug module itself works when called directly.

## Context Provided To The Skill

- stack: Elixir 1.16, Phoenix 1.7.11
- environment: production (discovered in security audit)
- logs: no errors — 200 returned as expected by the unauthenticated caller
- code excerpt:
```elixir
# router.ex
scope "/api", MyAppWeb.Api do
  pipe_through [:api, :require_admin]

  get "/admin/users",   AdminController, :users
  get "/admin/reports", AdminController, :reports
end

scope "/api", MyAppWeb.Api do
  pipe_through [:api]

  get "/admin/export",  AdminController, :export
  get "/health",        HealthController, :check
end
```
