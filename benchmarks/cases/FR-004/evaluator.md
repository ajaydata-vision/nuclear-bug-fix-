# Evaluator

## Metadata

- id: FR-004
- domain: frozen-runtime
- track: deploy-env
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyinstaller, bridge-script, frozen, meipass, spawn, helper

## Ground Truth

- root_cause: The parent resolves the helper with a frozen-aware path helper,
  but the helper script was never bundled into the packaged build.
- why_it_happens: Frozen-aware path logic does not help if PyInstaller never
  collects the child script. The packaged runtime points at the correct bundle
  location and the file is still absent.
- accepted_fix: Bundle the helper explicitly in the PyInstaller spec / collected
  data inputs, keep the frozen-aware resolver, and verify the helper is present
  in the packaged file tree.
- rejected_fix_patterns:
  - hardcode a developer machine path
  - call the missing helper from the source tree
  - treat `ENOENT` as a generic Node installation bug without checking the path

## Evidence Signals

- strongest_signal: The packaged log shows a frozen-aware helper path, but the
  extracted package tree still has no helper script at that location.
- strongest_alternative_explanation: The frozen path resolver is still wrong.
- why_alternative_is_wrong: The resolver already points at the bundle root and
  the extracted-file listing shows the helper is missing from the packaged
  build, not misresolved within it.

## Scoring Notes

- full_credit_conditions:
  - identifies missing helper bundling as the primary cause
  - explains why frozen-aware path resolution alone is insufficient
  - fixes by adding the helper to the packaged bundle and verifying presence
- partial_credit_conditions:
  - identifies packaging/bundling but not the missing-helper proof
- fail_conditions:
  - blames Node version mismatch without path evidence
  - suggests copying the helper manually beside the exe
  - rewrites the frozen path helper as if bundling were already proven correct
