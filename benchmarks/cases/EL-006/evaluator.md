# Evaluator

## Metadata

- id: EL-006
- domain: elixir-phoenix
- pattern: LiveView double mount
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: liveview, mount, double-mount, connected, side-effect, email

## Ground Truth

- root_cause: LiveView calls `mount/3` twice for every initial page load — once over HTTP (disconnected, connected?(socket) = false) to render the initial HTML, and once over WebSocket (connected, connected?(socket) = true) after the client connects. `Mailer.send_welcome_email(user)` runs on both mounts, sending two emails.
- why_it_happens: The LiveView lifecycle is: (1) HTTP request → mount → render HTML → response. (2) Client JavaScript → WebSocket connect → mount again → render again → live updates. Any side effect in mount without a `connected?(socket)` guard executes twice per page load.
- accepted_fix: Wrap the email send in `if connected?(socket) do` — the side effect runs only on the WebSocket mount.
- rejected_fix_patterns:
  - move email send to a controller action before the LiveView redirect (could work, but doesn't explain the LiveView bug)
  - use a database flag to track whether email was sent (workaround, not fix)
  - deduplicate at the mailer level (workaround, not fix)

## Evidence Signals

- strongest_signal: Email logged twice per signup; `send_welcome_email` only called once in mount; no loops
- pathognomonic_prove: Add `IO.puts("[DOUBLE-MOUNT-PROVE] mount called, connected=#{connected?(socket)}")` at top of mount — two lines appear in terminal for one browser page load
- strongest_alternative_explanation: Registration token verification called twice (page loaded twice)
- why_alternative_is_wrong: Logs show exact same timestamp for both sends; browser network tab shows one page load; user never double-clicked

## Scoring Notes

- full_credit_conditions:
  - identifies LiveView double mount (HTTP + WebSocket) as the cause
  - explains connected?/1 lifecycle
  - fix wraps send in `if connected?(socket) do`
  - mentions IO.puts double-mount Prove
- partial_credit_conditions:
  - identifies the double call but suggests deduplication at DB level
- fail_conditions:
  - blames the mailer or email provider
  - suggests the user refreshed the page
