# Evaluator

## Metadata

- id: FR-002
- domain: frozen-runtime
- track: evidence-limited
- difficulty: hard
- determinism: deterministic
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: pyinstaller, pyqt6, qt-plugin, evidence-limited, windows

## Ground Truth

- root_cause: The frozen build is missing or misresolving the Qt platform plugin/runtime path needed to initialize the `"windows"` platform plugin.
- why_it_happens: Qt startup depends on bundled plugin directories. A packaged build can work on a dev machine due to local environment leakage but fail on a clean machine if plugin collection/path setup is incomplete.
- accepted_fix: Use the correct PyInstaller Qt hooks/collectors, verify bundled plugin directories, and log the frozen plugin lookup path. Test on a clean Windows machine.
- rejected_fix_patterns:
  - tell users to reinstall the app without changing the bundle
  - blame generic Windows corruption
  - treat the issue as a normal Python import failure

## Evidence Signals

- strongest_signal: Exact Qt platform-plugin error plus empty logged plugin path in a frozen build.
- strongest_alternative_explanation: Customer machine has a broken GPU/driver stack.
- why_alternative_is_wrong: The failure occurs before UI startup and explicitly points at missing/invalid Qt platform plugin resolution.

## Scoring Notes

- full_credit_conditions:
  - identifies packaged Qt platform plugin resolution/bundling as the cause
  - explains why dev machine success does not clear a frozen plugin issue
  - fixes through proper plugin collection/path validation and clean-machine verification
- partial_credit_conditions:
  - suspects packaging but does not identify Qt plugin path specifically
- fail_conditions:
  - blames Python version mismatch without Qt evidence
  - recommends graphics driver updates as the primary fix
  - suggests reinstalling Windows
