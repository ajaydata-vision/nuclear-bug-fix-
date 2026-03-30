# Evaluator

## Metadata

- id: FE-011
- domain: frontend
- track: deploy-env
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: vite, env-var, build, production, VITE_prefix

## Ground Truth

- root_cause: Vite only exposes env variables prefixed with VITE_ to client-side code. Variables without this prefix are intentionally excluded from the browser bundle.
- why_it_happens: Vite strips non-prefixed variables from the client bundle as a security measure to prevent accidental exposure of server-side secrets. The VITE_ prefix is the explicit opt-in.
- accepted_fix: Rename to VITE_API_URL in .env files and update all references to import.meta.env.VITE_API_URL
- rejected_fix_patterns:
  - use process.env instead of import.meta.env
  - expose the variable via a separate config endpoint

## Evidence Signals

- strongest_signal: Variable is set in .env file but undefined at runtime; works in dev because Vite dev server handles differently
- strongest_alternative_explanation: .env.production file not loaded during build
- why_alternative_is_wrong: Other VITE_-prefixed variables from the same file are available; only the non-prefixed variable is missing

## Scoring Notes

- full_credit_conditions:
  - identifies missing VITE_ prefix
  - proposes renaming variable and all references
  - explains the security intent
- partial_credit_conditions:
  - identifies prefix requirement but does not explain why
- fail_conditions:
  - blames Vite bug
  - suggests injecting via window globals
