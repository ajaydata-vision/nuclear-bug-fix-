# Evaluator

## Metadata

- id: FR-003
- domain: frozen-runtime
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyinstaller, appdata, permissions, writable-path, session

## Ground Truth

- root_cause: The packaged app writes mutable auth/session data under the install directory beside the executable, which is not reliably writable for normal users under `Program Files`.
- why_it_happens: Frozen apps must separate immutable program files from mutable user state. Install paths are often read-only, so session persistence silently fails or raises permission errors.
- accepted_fix: Store mutable state under a per-user writable path such as `%APPDATA%` or `%LOCALAPPDATA%`, create it explicitly, and point the bridge there.
- rejected_fix_patterns:
  - require the whole app to run as administrator
  - keep writing beside the exe and ignore the error
  - blame WhatsApp auth expiry instead of the write failure

## Evidence Signals

- strongest_signal: Logs show the app writing auth state under `Program Files` and failing with `PermissionError`, followed by lost session persistence.
- strongest_alternative_explanation: WhatsApp invalidates the session token on each launch.
- why_alternative_is_wrong: The session never persisted locally because the write path is not writable; the app log already proves local persistence failure.

## Scoring Notes

- full_credit_conditions:
  - identifies non-writable install-dir state storage as the root cause
  - explains why packaged apps must use per-user writable paths
  - fixes by moving auth/session data to `%APPDATA%`/`%LOCALAPPDATA%`
- partial_credit_conditions:
  - identifies a permissions issue but suggests admin rights instead of the correct state location
- fail_conditions:
  - blames QR timeout or auth expiry
  - suggests repeated re-login as acceptable
  - rewrites bridge auth logic without moving the storage path
