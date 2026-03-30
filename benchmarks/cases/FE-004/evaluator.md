# Evaluator

## Metadata

- id: FE-004
- domain: frontend
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: false
- tags: tailwind, css-purge, production, dynamic-classes, build

## Ground Truth

- root_cause: Tailwind's content scanner cannot detect dynamically constructed class strings so the purge step removes them from the production bundle.
- why_it_happens: Tailwind scans source files at build time and removes classes not found as complete strings. A template literal like text-${color}-500 is never a complete class string so purge removes it.
- accepted_fix: Use complete class names in code or safelist the classes: safelist: ['text-red-500', 'text-green-500'] in tailwind.config.js
- rejected_fix_patterns:
  - disable purge entirely
  - use inline styles as workaround without explaining root cause

## Evidence Signals

- strongest_signal: Styles present in dev build but absent in production with identical markup
- strongest_alternative_explanation: CSS specificity conflict from other stylesheets
- why_alternative_is_wrong: The class is fully missing from the production stylesheet, not being overridden

## Scoring Notes

- full_credit_conditions:
  - identifies Tailwind purge removing dynamically constructed classes
  - proposes safelist or complete class name strings
  - explains why template literals break the scanner
- partial_credit_conditions:
  - identifies build-time class removal but does not explain dynamic construction
- fail_conditions:
  - blames browser caching
  - suggests using !important
