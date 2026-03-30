# Evaluator

## Metadata

- id: VE-003
- domain: version-external-intelligence
- track: regression-version
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: axios, multipart, boundary, changelog, known-bug

## Ground Truth

- root_cause: The exact Axios upgrade introduced a known multipart boundary regression in the browser upload path.
- why_it_happens: The request no longer sends the boundary correctly for this version and request style.
- accepted_fix: Upgrade to a fixed Axios version or stop forcing the multipart header so the browser sets the boundary correctly.
- rejected_fix_patterns:
  - blame the backend parser first
  - manually concatenate a fake boundary
  - ignore the version regression clue

## Evidence Signals

- strongest_signal: Reverting the Axios version alone restores correct upload behavior
- strongest_alternative_explanation: Multer or backend multipart parsing broke
- why_alternative_is_wrong: Backend behavior did not change and the regression is strictly version-linked on the client

## Scoring Notes

- full_credit_conditions:
  - identifies version-specific client regression
  - recommends checking changelog/issues or upgrading
  - does not anchor on server parsing only
- partial_credit_conditions:
  - spots boundary issue but misses version intelligence
- fail_conditions:
  - blames server code only
  - keeps the broken client version and invents unsafe header hacks
