# Evaluator

## Metadata

- id: FR-A01
- domain: frozen-runtime
- track: deploy-env
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyinstaller, frozen, meipass, path-resolution, subprocess, node

## Ground Truth

- root_cause: The packaged runtime resolves the bridge script using source-style `__file__` assumptions instead of the frozen bundle layout, so the spawn path does not exist in the packaged app.
- why_it_happens: In PyInstaller, bundled resources/scripts may live under the frozen extraction layout. Source-relative paths are not reliable unless resource resolution handles frozen mode explicitly.
- accepted_fix: Resolve bundled resources/scripts via a frozen-aware helper that uses `sys._MEIPASS` (or explicit collected-data paths) when frozen, and source-relative paths otherwise.
- rejected_fix_patterns:
  - hardcode a developer machine path to the bridge script
  - retry spawn forever
  - blame Node installation without checking the resolved script path

## Evidence Signals

- strongest_signal: App works from source, fails only when frozen, and the packaged evidence shows the bridge asset exists in the bundle but the resolved path points to the wrong location.
- strongest_alternative_explanation: Node is not installed on the machine.
- why_alternative_is_wrong: The error is ENOENT for the script path, not the `node` executable itself, and the packaged path resolution is already logged.

## Scoring Notes

- full_credit_conditions:
  - identifies source-style path resolution as the packaged-only failure
  - explains why frozen mode needs different resource/script resolution
  - fixes with a frozen-aware path helper / bundled data resolution
- partial_credit_conditions:
  - identifies packaged path mismatch but only suggests changing cwd
- fail_conditions:
  - blames Node version mismatch without path evidence
  - suggests copying the script manually beside the exe as the main fix
  - rewrites bridge protocol code
