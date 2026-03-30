# Benchmark Results — Iteration 1

Run against all 20 starter cases. Scored against evaluator.md ground truth.

## Scores

| Case    | RC/25 | Fix/20 | 1st/40 | Ver/10 | Ev/5 | Total | Track |
|---------|------:|-------:|-------:|-------:|-----:|------:|-------|
| BE-003  |    25 |     20 |     40 |     10 |    5 |   100 | distributed-multi-factor |
| BE-009  |    25 |     20 |     40 |     10 |    5 |   100 | intermittent-race |
| BE-020  |    25 |     20 |     40 |     10 |    5 |   100 | deploy-env |
| DE-001  |    25 |     20 |     40 |     10 |    5 |   100 | deploy-env |
| DE-002  |    25 |     20 |     40 |     10 |    5 |   100 | deploy-env |
| DE-006  |    25 |     20 |     40 |     10 |    5 |   100 | deploy-env |
| FE-001  |    20 |     20 |     30 |      6 |    5 |    81 | bohrbug-core |
| FE-008  |    25 |     20 |     40 |     10 |    5 |   100 | intermittent-race |
| **FE-019** | **10** | **10** | **0** | **4** | **5** | **29** | deploy-env |
| IN-002  |    25 |     20 |     40 |     10 |    5 |   100 | distributed-multi-factor |
| IN-009  |    25 |     20 |     40 |     10 |    5 |   100 | distributed-multi-factor |
| IN-017  |    25 |     20 |     40 |     10 |    5 |   100 | deploy-env |
| MO-001  |    25 |     20 |     40 |     10 |    5 |   100 | bohrbug-core |
| MO-005  |    25 |     20 |     40 |     10 |    5 |   100 | bohrbug-core |
| RC-001  |    25 |     20 |     40 |     10 |    5 |   100 | intermittent-race |
| RC-002  |    25 |     20 |     40 |     10 |    5 |   100 | intermittent-race |
| RC-008  |    25 |     20 |     40 |     10 |    5 |   100 | intermittent-race |
| **RC-018** | **15** | **15** | **20** | **6** | **5** | **61** | deploy-env |
| VE-003  |    25 |     20 |     40 |     10 |    5 |   100 | regression-version |
| VE-006  |    25 |     20 |     40 |     10 |    5 |   100 | regression-version |

**Mean: 93.5 / 100 | 90+: 17/20 | Below 80: 2 cases**

## Failure Analysis

### FE-019 — 29/100 (FAIL)
Signal "hard refresh fixes it" = service worker, not CDN.
Skill has no disambiguation rule between SW and CDN cache symptoms.
Would likely prescribe CDN invalidation or content-hash strategy — both wrong.
Service worker fix (update cache strategy, version cache name on activate) not triggered.

Gap: Add SW vs CDN disambiguation rule to frontend-patterns.md.

### RC-018 — 61/100 (PARTIAL)
Skill identifies pod not truly ready but misses the precise mechanism:
readiness probe checks HTTP response not actual Redis/PostgreSQL connectivity.
Would say "add startup delay" rather than "fix the readiness endpoint to check deps."
Gap: Add K8s readiness vs liveness probe pattern to skill.

### FE-001 — 81/100 (MINOR)
Correct fix identified but does not explicitly reject suppressHydrationWarning.
Evaluator requires this rejection for full credit.
Gap: Add suppressHydrationWarning antipattern note to hydration pattern.

## Track Performance

| Track                   | Cases | Mean  |
|-------------------------|------:|------:|
| intermittent-race       |     5 |  100  |
| distributed-multi-factor|     3 |  100  |
| regression-version      |     2 |  100  |
| bohrbug-core            |     3 |  93.7 |
| deploy-env              |     7 |  80.1 |

Weakest track: deploy-env. Both failures come from infrastructure-specific
nuance (K8s probe semantics, SW vs CDN disambiguation) not covered precisely.

## Fixes Required Before Iteration 2

1. FE-019: Add service worker vs CDN disambiguation to frontend-patterns.md
2. RC-018: Add K8s readiness probe pattern to integration-patterns.md
3. FE-001: Add suppressHydrationWarning antipattern note
