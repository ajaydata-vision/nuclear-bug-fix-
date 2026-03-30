# Case Template

Use one directory per benchmark case.

```text
benchmarks/cases/<case-id>/
  prompt.md
  evaluator.md
  verify.md
  assets/
```

## `prompt.md`

This is the user-visible prompt only. It is the exact input shown to the skill.

Recommended structure:

```markdown
# <case-id>: <short title>

## User Prompt
<what the user says>

## Context Provided To The Skill
- stack:
- versions:
- environment:
- logs:
- code excerpt:
- reproduction:
```

## `evaluator.md`

This is hidden from the skill and used for scoring.

Recommended structure:

```markdown
# Evaluator

## Metadata
- id:
- domain:
- track:
- difficulty:
- determinism:
- one_shot_eligible:
- requires_external_intelligence:
- requires_runtime_access:
- requires_log_access:
- tags:

## Ground Truth
- root_cause:
- why_it_happens:
- accepted_fix:
- rejected_fix_patterns:

## Evidence Signals
- strongest_signal:
- strongest_alternative_explanation:
- why_alternative_is_wrong:

## Scoring Notes
- full_credit_conditions:
- partial_credit_conditions:
- fail_conditions:
```

## `verify.md`

This is the acceptance test for the case.

Recommended structure:

```markdown
# Verification

## Before Fix
- how to trigger the bug
- expected failing output

## After Fix
- how to rerun the same scenario
- expected passing output

## Regression Checks
- specific edge cases to confirm
```

## Case Writing Rules

- one primary bug per case unless the case is explicitly tagged `multi-factor`
- exact versions are mandatory
- accepted fix must be minimal
- evaluator must name at least one strong but wrong alternative explanation
- every case must have an objective pass/fail condition
- if a case needs external intelligence, the answer key must include the source class:
  docs, changelog, RFC, issue tracker, CVE, compatibility matrix

