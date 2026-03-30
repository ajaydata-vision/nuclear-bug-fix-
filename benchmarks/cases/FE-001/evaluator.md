# Evaluator

## Metadata

- id: FE-001
- domain: frontend
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: ssr, hydration, react, nextjs, nondeterministic-render

## Ground Truth

- root_cause: A nondeterministic value is generated during SSR render, so server
  and client HTML diverge before hydration.
- why_it_happens: `Date.now()` executes once on the server and again on the
  client, producing different text nodes.
- accepted_fix: Move timestamp generation to a client-only effect or pass a
  stable value from the server as a prop.
- rejected_fix_patterns:
  - add random delays
  - blame CSS or Tailwind
  - use `suppressHydrationWarning` as the primary fix

## Evidence Signals

- strongest_signal: Server and client render different timestamp text
- strongest_alternative_explanation: Browser extension or third-party script mutates DOM
- why_alternative_is_wrong: The mismatch is already visible in the raw rendered
  text before any extension-specific evidence appears

## Scoring Notes

- full_credit_conditions:
  - names nondeterministic SSR render as the cause
  - proposes a stable server prop or client-only computation
  - explicitly rejects `suppressHydrationWarning` as a real fix
- partial_credit_conditions:
  - identifies hydration mismatch correctly but gives a generic fix only
- fail_conditions:
  - blames bundler, CSS, or state management
  - proposes only hiding the warning
