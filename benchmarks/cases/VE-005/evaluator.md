# Evaluator

## Metadata

- id: VE-005
- domain: version-external-intelligence
- track: regression-version
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: node, minimum-version, framework-requirement, syntax-error, esm

## Ground Truth

- root_cause: Next.js 14 requires Node.js 18.17 or higher. Node 16 lacks APIs and syntax features used internally by Next.js 14.
- why_it_happens: Next.js 14 uses features not available in Node 16 (e.g., Fetch API, newer V8 syntax). The cryptic syntax error is a symptom of running framework code that targets a newer Node runtime.
- accepted_fix: Upgrade Node.js to 18.17+ (LTS) on all machines and in CI. Add engines field to package.json: { "engines": { "node": ">=18.17" } }
- rejected_fix_patterns:
  - downgrade Next.js to 12 to match Node 16
  - add @babel/polyfill for missing features

## Evidence Signals

- strongest_signal: Error is a syntax/API error inside Next.js internals not user code; different Node versions produce different results; Next.js docs list minimum Node version
- strongest_alternative_explanation: npm install corruption
- why_alternative_is_wrong: Deleting node_modules and reinstalling reproduces the same error; the issue is Node version not package integrity

## Scoring Notes

- full_credit_conditions:
  - identifies Node 16 below Next.js 14 minimum (18.17+)
  - proposes Node upgrade and engines field
  - cites Next.js docs or release notes
- partial_credit_conditions:
  - identifies version mismatch but does not specify the minimum version
- fail_conditions:
  - suggests using npx instead of node
  - blames Next.js installation
