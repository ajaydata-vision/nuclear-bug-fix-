# Benchmark Suite

This directory is the missing proof layer for `nuclear-bug-fix`.

The skill can only claim high confidence if it can solve a large set of
reproducible bugs under controlled evaluation. The goal of this suite is not
to measure writing quality. It is to measure whether the skill:

1. identifies the real root cause
2. proposes the minimally correct fix
3. avoids confident wrong answers
4. verifies the fix under the same conditions that caused the bug

## What A Good Benchmark Looks Like

Each benchmark case should include:

- a realistic user prompt
- exact stack and version numbers
- a reproducible failing scenario
- the assets needed to inspect the bug
- a hidden evaluator answer key
- a minimal accepted fix
- a verification command or checklist

Each case should be small enough to evaluate clearly, but realistic enough to
represent a true production bug pattern.

## Directory Shape

Recommended layout:

```text
benchmarks/
  README.md
  CASE_TEMPLATE.md
  COVERAGE_MATRIX.md
  BENCHMARK_BACKLOG.md
  index.yaml
  cases/
    <case-id>/
      prompt.md
      evaluator.md
      assets/
      verify.md
```

## Tracks

The suite should be split into tracks, because not all bugs are equally
one-shot solvable.

- `bohrbug-core`: deterministic, reproducible, one primary root cause
- `regression-version`: bug introduced by dependency, runtime, browser, or API changes
- `deploy-env`: wrong code running, stale assets, bad config, replica lag, partial rollout
- `intermittent-race`: timing, concurrency, startup, flaky tests, shared-state races
- `distributed-multi-factor`: queue, webhook, gateway, ETL, saga, cache, service interactions
- `evidence-limited`: limited logs, limited code, or only symptom + stack trace available

## Scoring Model

Score each case out of 100.

- `40` First-shot resolution
  Definition: the first proposed fix resolves the benchmark under the benchmark's
  verification conditions.
- `25` Root cause accuracy
  Definition: the primary cause named by the skill matches the evaluator answer key.
- `20` Fix accuracy
  Definition: the proposed fix is minimal, correct, and does not rely on unrelated rewrites.
- `10` Verification quality
  Definition: the skill defines a real check that would prove the bug is gone.
- `5` Evidence discipline
  Definition: the skill uses the available evidence instead of guessing.

Penalties:

- `-40` confident wrong answer
- `-25` root cause mismatch with a superficially plausible fix
- `-20` shotgun rewrite when a local fix exists
- `-15` no verification or unverifiable claim
- `-10` revisits disproven path without new evidence

## Confidence Gates

Do not count a result as high-confidence unless the benchmark answer shows:

- reproduced failure or clear reproduction conditions
- correct code or system under inspection
- strongest competing explanation addressed
- fix scoped to the proven failure mechanism
- verification under the same conditions as the failure

## Suite Targets

Recommended minimum sizes:

- `30` core Bohrbugs
- `20` version/regression cases
- `20` deploy/environment cases
- `20` intermittent/race cases
- `20` distributed or multi-factor cases
- `20` evidence-limited cases

That gives a first credible suite of `130` cases.

Recommended mature target:

- `250+` cases across all tracks

## What Will Move The Score

If you want to push the skill toward `90%+`, the most important benchmark mix is:

1. deterministic one-shot eligible bugs
2. version regression bugs requiring external intelligence
3. deploy/config bugs where the code is not the real problem
4. intermittent bugs with controlled amplification
5. distributed failures where the first guess is usually wrong

The benchmark suite must punish false confidence, not just reward plausible fixes.

