# Verification

## After Fix

```elixir
scope "/api", MyAppWeb.Api do
  pipe_through [:api, :require_admin]

  get "/admin/users",   AdminController, :users
  get "/admin/reports", AdminController, :reports
  get "/admin/export",  AdminController, :export  # moved here
end

scope "/api", MyAppWeb.Api do
  pipe_through [:api]

  get "/health", HealthController, :check
end
```

## Regression Checks

- GET /api/admin/export without token: HTTP 401
- GET /api/admin/export with valid admin token: HTTP 200, data returned
- GET /api/admin/users without token: HTTP 401 (unchanged)
- GET /api/health without token: HTTP 200 (unchanged — health check remains public)
