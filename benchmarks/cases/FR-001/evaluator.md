# Evaluator

## Metadata

- id: FR-001
- domain: frozen-runtime
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: pyinstaller, hidden-import, dynamic-import, google-auth

## Ground Truth

- root_cause: PyInstaller did not bundle a dynamically reached dependency needed by the Google auth path, so the module exists in development but is missing from the frozen archive.
- why_it_happens: Static analysis misses some optional or late imports. The failing path is only executed when that settings screen is opened, so startup succeeds.
- accepted_fix: Add the missing hidden import / collection hook for the auth dependency and rebuild the bundle.
- rejected_fix_patterns:
  - install the dependency manually on the target machine and call it fixed
  - catch the import error and ignore it
  - blame user credentials when the traceback shows a missing module

## Evidence Signals

- strongest_signal: Source environment works, packaged build fails only when a feature-specific import path executes, and the traceback is a clear `ModuleNotFoundError`.
- strongest_alternative_explanation: The settings page is loading the wrong credentials file.
- why_alternative_is_wrong: Wrong credentials would fail during auth/session construction, not as a missing Python module import.

## Scoring Notes

- full_credit_conditions:
  - identifies a PyInstaller hidden-import/dynamic-import miss
  - explains why the feature-specific path fails only in the packaged build
  - fixes with hidden import / hook changes and rebuild
- partial_credit_conditions:
  - identifies packaged import miss but does not explain why startup still works
- fail_conditions:
  - blames OAuth credentials
  - suggests retrying the same import
  - blames Windows PATH
