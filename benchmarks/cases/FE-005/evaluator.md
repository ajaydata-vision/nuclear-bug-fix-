# Evaluator

## Metadata

- id: FE-005
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: css, z-index, stacking-context, modal, transform

## Ground Truth

- root_cause: The sidebar creates a new stacking context via transform: translateZ(0), making z-index comparisons happen within that context rather than against the document root.
- why_it_happens: CSS properties like transform, opacity, filter, and will-change create new stacking contexts. A child of that context cannot stack above elements outside it regardless of z-index value.
- accepted_fix: Remove transform: translateZ(0) from the sidebar, or render the modal at the document root level (portal) outside any stacking context.
- rejected_fix_patterns:
  - increase modal z-index further
  - use !important on z-index

## Evidence Signals

- strongest_signal: Higher z-index has no effect; an ancestor element uses a CSS property that creates a stacking context
- strongest_alternative_explanation: Missing position: fixed on modal
- why_alternative_is_wrong: position: fixed is already set; the issue is stacking context containment not positioning

## Scoring Notes

- full_credit_conditions:
  - identifies stacking context created by transform
  - proposes portal or removing transform
  - explains why z-index value is irrelevant here
- partial_credit_conditions:
  - identifies stacking context but not which property causes it
- fail_conditions:
  - suggests higher z-index
  - blames browser rendering bug
