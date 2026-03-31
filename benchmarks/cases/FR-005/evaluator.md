# Evaluator

## Metadata

- id: FR-005
- domain: frozen-runtime
- track: intermittent-race
- difficulty: hard
- determinism: intermittent
- one_shot_eligible: false
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: pyinstaller, onefile, extraction, startup-race, child-process

## Ground Truth

- root_cause: The onefile build assumes bundled child resources are ready before
  extraction and runtime initialization have fully completed, so the helper is
  launched too early on the first run.
- why_it_happens: Onefile apps extract to a temp runtime directory. Early child
  launch or source-style path resolution can race the extraction lifecycle and
  fail on the first startup only.
- accepted_fix: Resolve the child from the frozen runtime layout and delay child
  launch until the onefile extraction/runtime path is ready.
- rejected_fix_patterns:
  - add blind startup sleeps
  - ignore onefile vs onedir differences
  - blame Windows Defender without path/timing evidence

## Evidence Signals

- strongest_signal: Failure appears only on first launch after install, and logs
  show the child is launched immediately while extraction/runtime paths are
  still stabilizing.
- strongest_alternative_explanation: The helper binary is missing from the build.
- why_alternative_is_wrong: The second launch often succeeds, which points to
  timing/extraction readiness rather than a permanently missing binary.

## Scoring Notes

- full_credit_conditions:
  - identifies onefile extraction/startup timing as the problem
  - explains why first launch differs from later launches
  - fixes by waiting for or correctly resolving the frozen runtime before launch
- partial_credit_conditions:
  - identifies a packaged timing issue but only suggests sleeps
- fail_conditions:
  - blames helper packaging alone
  - suggests retrying the child launch forever
  - ignores the onefile extraction lifecycle
