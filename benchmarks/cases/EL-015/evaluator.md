# Evaluator

## Metadata

- id: EL-015
- domain: elixir-phoenix
- pattern: Phoenix Plug pipeline auth bypass
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: phoenix, plug, pipeline, auth, scope, pipe_through, router

## Ground Truth

- root_cause: `/api/admin/export` is defined in the second `scope "/api"` block which uses `pipe_through [:api]` — without `:require_admin`. The first scope correctly uses `pipe_through [:api, :require_admin]` for `/admin/users` and `/admin/reports`. The export endpoint is in the wrong scope — it bypasses the admin authentication plug entirely.
- why_it_happens: Phoenix applies plugs in pipeline order, per scope. A route only receives the plugs from the `pipe_through` of its own scope block. Routes in different scope blocks have completely independent pipelines. Having two scope blocks for the same path prefix (`"/api"`) is valid Phoenix — the router applies each independently.
- accepted_fix: Move `get "/admin/export"` into the first scope block that has `pipe_through [:api, :require_admin]`.
- rejected_fix_patterns:
  - add authentication check inside the controller action (works as a patch but leaves the architectural problem)
  - merge all routes into one scope (correct approach — move the route)

## Evidence Signals

- strongest_signal: Two `scope "/api"` blocks with different pipe_through; export route in the unauthenticated scope
- pathognomonic_prove: `grep -n "export\|pipe_through\|scope" lib/my_app_web/router.ex` confirms route is in scope with `pipe_through [:api]` only; `curl -I http://localhost:4000/api/admin/export` returns 200 without auth header
- strongest_alternative_explanation: RequireAdmin plug has a bug allowing all requests through
- why_alternative_is_wrong: Other admin endpoints (/admin/users, /admin/reports) correctly return 401; the plug works — the route is simply not in the authenticated scope

## Scoring Notes

- full_credit_conditions:
  - identifies /api/admin/export in wrong scope (pipe_through [:api] without :require_admin)
  - explains that Phoenix applies pipe_through per scope block
  - fix moves export route into the authenticated scope
  - mentions grep router.ex or curl test as the Prove
- partial_credit_conditions:
  - identifies the missing auth but suggests fixing in controller instead of router
- fail_conditions:
  - blames the RequireAdmin plug implementation
  - suggests adding a before_action callback
