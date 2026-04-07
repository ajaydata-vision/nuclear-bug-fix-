# Evaluator

## Metadata

- id: EL-A02
- domain: elixir-phoenix
- pattern: LiveView double mount (test environment gap)
- track: adversarial
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: liveview, mount, double-mount, connected, test, live_view_test, false-passing-test

## Ground Truth

- root_cause: The fix is correct and the test correctly verifies the fix in the test environment. The test passes because LiveView test helpers (`live/2`) call `mount/3` once with `connected?(socket) = true` — the test environment skips the HTTP (disconnected) mount and connects directly. This means the `if connected?(socket)` guard always evaluates to `true` in tests, and the test only verifies the connected-mount path.

  The SECOND email in production comes from a different code path that is NOT in the LiveView. The second log line `"Sending welcome email"` has no `connected=` part — it is not from the LiveView code at all. There is another code path (controller, context callback, Oban job, or Phoenix.Channel) that also calls `Mailer.send_welcome_email(user)` independently of the LiveView.

  The production logs prove this: the first email has `connected=true` (from the fixed LiveView code), the second has no `connected=` suffix (from a different code path not modified by the fix).

- why_test_passes: LiveView test helpers mount once with connected?=true. The disconnected (HTTP) mount never occurs in tests. Tests cannot detect double-mount bugs from connected? guards alone — they only verify the connected path.

- accepted_fix: Find and remove the second call to `Mailer.send_welcome_email`. Search all callers: `grep -r "send_welcome_email" lib/`. The duplicate call is in a non-LiveView code path.

## Scoring Notes

- full_credit_conditions:
  - identifies that LiveView tests use connected?=true only — they cannot detect the disconnected mount
  - explains that the second email comes from a DIFFERENT code path (not the LiveView)
  - evidence: second log line has no "connected=" suffix — different code path
  - fix: search all callers of send_welcome_email and remove the duplicate
  - does NOT tell developer to revert the LiveView fix (it is correct)
- partial_credit_conditions:
  - identifies the test gap (connected? always true in tests) but doesn't identify the second code path
  - suggests the fix is wrong and recommends reverting
- fail_conditions:
  - says the deployed fix is incorrect
  - says to add a database flag to prevent duplicate sends (workaround, misses root cause)
  - blames the test framework without explaining why tests cannot catch this
