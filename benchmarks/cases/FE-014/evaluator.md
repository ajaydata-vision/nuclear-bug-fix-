# Evaluator

## Metadata

- id: FE-014
- domain: frontend
- track: bohrbug-core
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: true
- requires_runtime_access: false
- requires_log_access: true
- tags: safari, browser-compat, lookbehind, regex, cross-browser

## Ground Truth

- root_cause: Lookbehind assertions in regular expressions were not supported in Safari until Safari 16.4 (May 2023). Older Safari versions throw on parsing the regex.
- why_it_happens: JavaScript lookbehind (?<=...) and (?<!...) are ES2018 features. Safari's JavaScriptCore engine added support later than V8 and SpiderMonkey.
- accepted_fix: Rewrite the regex without lookbehind, or add a feature detection check and provide a fallback validation path for older Safari.
- rejected_fix_patterns:
  - add 'use strict' directive
  - switch to a different regex library without explaining the compat issue

## Evidence Signals

- strongest_signal: Error message explicitly references regex group specifier; only Safari is affected
- strongest_alternative_explanation: Safari blocking the script due to CSP
- why_alternative_is_wrong: CSP violations appear as CSP errors; this is a JavaScript TypeError from regex parsing

## Scoring Notes

- full_credit_conditions:
  - identifies lookbehind as unsupported in Safari versions
  - proposes rewrite or feature detection
  - cites caniuse or MDN for support table
- partial_credit_conditions:
  - identifies Safari compat issue but does not specify the exact feature
- fail_conditions:
  - adds try/catch to silence error without fixing the regex
  - blames Safari bug
