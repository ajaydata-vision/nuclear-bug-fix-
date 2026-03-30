# Evaluator

## Metadata

- id: VE-001
- domain: version-external-intelligence
- track: regression-version
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: npm, peer-dependency, version-mismatch, react, package-conflict

## Ground Truth

- root_cause: react-query v3 does not officially support React 18 and has known compatibility issues causing hooks to silently fail.
- why_it_happens: react-query v3 was built before React 18's concurrent mode changes. The peer dependency warning signals incompatibility. The fix is upgrading to TanStack Query v5 which fully supports React 18.
- accepted_fix: Upgrade to @tanstack/react-query v5 which is the React 18 compatible version of react-query.
- rejected_fix_patterns:
  - downgrade React to 17 to match the peer dependency
  - ignore the peer dependency warning

## Evidence Signals

- strongest_signal: npm install warns about peer dependency mismatch; hooks silently fail after React 18 upgrade
- strongest_alternative_explanation: QueryClient not provided via QueryClientProvider
- why_alternative_is_wrong: The issue started on React 18 upgrade with no other code changes; peer dependency warning specifically names React 18 incompatibility

## Scoring Notes

- full_credit_conditions:
  - identifies react-query v3 incompatibility with React 18
  - proposes upgrading to @tanstack/react-query v5
  - cites the npm peer dependency warning as the signal
- partial_credit_conditions:
  - identifies version mismatch but proposes downgrading React
- fail_conditions:
  - ignores peer dependency warning
  - suggests reinstalling node_modules
