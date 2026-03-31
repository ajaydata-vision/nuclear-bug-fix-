# Evaluator

## Metadata

- id: BI-004
- domain: bridge-adapters
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: bridge-version, packaged-build, protocol-version, parent-child, node-python

## Ground Truth

- root_cause: The packaged parent and child bridge are running different release
  versions or protocol versions, so the handshake succeeds superficially but the
  wire protocol no longer matches after startup.
- why_it_happens: Packaged parent and child are separate artifacts. If one side
  is not rebuilt or version-stamped with the other, they can appear connected
  while silently disagreeing on message format or lifecycle behavior.
- accepted_fix: Stamp and ship matching parent/child versions, validate the child
  version/protocol during handshake, and fail fast if they differ.
- rejected_fix_patterns:
  - ignore the version mismatch because the handshake "worked"
  - add arbitrary reconnects without checking protocol compatibility
  - patch the UI to hide the missing events

## Evidence Signals

- strongest_signal: Logs explicitly show parent and child versions/protocols do
  not match, and the bridge only fails in packaged mode.
- strongest_alternative_explanation: Network instability is dropping events after
  startup.
- why_alternative_is_wrong: The mismatch is already visible before transport
  failures would matter, and the same packaged build is the common factor.

## Scoring Notes

- full_credit_conditions:
  - identifies version/protocol mismatch between parent and child as the cause
  - explains why packaged builds are more likely to drift than source runs
  - fixes by validating/stamping matching versions at startup
- partial_credit_conditions:
  - identifies a packaged build mismatch but does not tie it to protocol/version
- fail_conditions:
  - blames websocket reliability without version evidence
  - suggests more retries instead of compatibility checks
  - ignores the mismatch and only changes UI handling
