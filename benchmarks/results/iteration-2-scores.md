# Benchmark Results — Iteration 2

Evaluated all 100 cases. Claude applies nuclear-bug-fix methodology; scored against evaluator.md ground truth.

**Mean: 92.3/100 | Perfect (100): 52 | High (85): 45 | Medium (70): 3 | Low (<70): 0**

Iteration 1 mean (20 cases): 93.5/100 — Iteration 2 mean (100 cases): 92.3/100. Consistent.

## Scores By Track

| Track | n | Mean | Assessment |
|---|---:|---:|---|
| bohrbug-core | 36 | 94.2 | Strong — deterministic bugs with clear signals |
| deploy-env | 29 | 94.3 | Strong — environment patterns well covered |
| distributed-multi-factor | 9 | 91.7 | Good — complex cases, multi-step diagnosis |
| intermittent-race | 19 | 88.9 | Good — race playbook carries most cases |
| regression-version | 7 | 85.0 | Weakest — deep changelog dives required |

## Cases Scoring Below 100

| Case | Score | Root Cause Of Score Reduction |
|---|---:|---|
| RC-015 | 70 | Optimistic update desync — TanStack Query onMutate/onError pattern, no reference coverage |
| RC-018 | 70 | K8s readiness probe semantics — no dedicated K8s health probe reference file |
| VE-007 | 70 | Mongoose 7 null update behavior — very obscure breaking change, deep changelog dive required |
| BE-004 | 85 | Timeout/completion race — async job + idempotency key together is slightly complex |
| BE-006 | 85 | SameSite=Strict cross-subdomain — precise cookie semantics explanation needed |
| BE-008 | 85 | Wrong DATABASE_URL (.env vs vault) — finding the mismatch slightly subtle |
| BE-012 | 85 | Local disk vs shared storage — multi-instance routing adds deploy-env complexity |
| BE-015 | 85 | Module-level shared state — security issue, intermittent, subtle |
| BE-018 | 85 | Outbound VPC firewall — infra fix, requires curl from prod server to confirm |
| DE-002 | 85 | CDN vs SW disambiguation — Cat12 helps but careful signal reading needed |
| DE-006 | 85 | Mixed version partial rollout — requires checking all instances |
| FE-001 | 85 | SSR nondeterministic value — subtle hydration knowledge needed |
| FE-009 | 85 | WS handler race — race window subtle, only fast networks |
| FE-014 | 85 | Lookbehind regex Safari — MDN/caniuse external intel required |
| FE-019 | 85 | Service worker cache stale — Cat12 added, 85 conservatively |
| FE-020 | 85 | Date space vs T separator Firefox — external intel confirms spec |
| IN-006 | 85 | Per-message DB query bottleneck — throughput math needed |
| IN-008 | 85 | Schema drift field renamed — contract testing gap |
| IN-009 | 85 | Cascade failure missing timeout — multi-factor tracing |
| IN-010 | 85 | API Gateway stripping Authorization — infra knowledge |
| IN-014 | 85 | HTTP probe vs gRPC port — protocol + K8s probe types |
| IN-015 | 85 | DLQ full no consumer — multi-factor backpressure chain |
| IN-016 | 85 | ALB idle timeout drops gRPC — infra timeout correlation |
| IN-017 | 85 | Mutable Docker tag IfNotPresent — deploy-env/integration overlap |
| IN-018 | 85 | Connection pool exhaustion — Cat10 now provides the math |
| IN-019 | 85 | Retry storm on 429 — backoff+jitter+circuit-breaker all needed |
| MO-001 | 85 | Native module not linked — React Native build knowledge |
| MO-003 | 85 | Push token not refreshed on reinstall — tokenSentToServer subtle |
| MO-004 | 85 | Large bitmap OOM Android — profiling required |
| MO-005 | 85 | Offline sync reconnect — React Native NetInfo pattern |
| MO-006 | 85 | Deep link before navigator ready — cold vs warm start timing |
| MO-008 | 85 | iOS force-quit blocks background — OS behavior, not a code bug |
| RC-004 | 85 | Cache stampede — distributed lock or probabilistic expiry |
| RC-005 | 85 | WS broadcast before HTTP response — subtle ordering race |
| RC-006 | 85 | Deadlock opposite lock order — canonical ordering needed |
| RC-007 | 85 | CLS context not isolated — Node.js async context knowledge |
| RC-009 | 85 | Concurrent migration K8s — init container or advisory lock |
| RC-010 | 85 | Concurrent file writes — process-safe vs thread-safe |
| RC-011 | 85 | Session fixation — Cat12 now covers session.regenerate() |
| RC-012 | 85 | Batch charge race — SELECT FOR UPDATE SKIP LOCKED |
| RC-013 | 85 | Distributed lock no TTL — Cat11 now covers SET NX EX |
| RC-016 | 85 | WS reconnect accumulates handlers — old socket not closed |
| RC-017 | 85 | Promise.all shared object race — JS async interleaving |
| VE-001 | 85 | react-query v3 + React 18 — npm peer dep warning is signal |
| VE-002 | 85 | pydantic v2 transitive dep — ImportError on moved class |
| VE-003 | 85 | Axios multipart boundary bug — version changelog lookup |
| VE-004 | 85 | Chrome 121 Vibration API removed — MDN/caniuse needed |
| VE-006 | 85 | OAuth 2.0 PKCE — RFC 7636 compliance check |

## Actionable Gaps (3 cases at 70)

### RC-015 — Optimistic UI desync (TanStack Query pattern)
The skill lacks a reference pattern for the TanStack Query recommended flow:
`onMutate` (save previous state) → `onError` (rollback) → `onSettled` (invalidate).
Without this, the skill may suggest only frontend fixes (debounce) not the state management fix.

**Fix:** Add TanStack Query optimistic update pattern to `references/frontend-patterns.md` Category 6.

### RC-018 — K8s readiness probe semantics
The skill has no reference for the distinction between readiness probes checking
HTTP liveness vs actual dependency health (Redis ping, DB query).
The fix (checking real dependencies in /readyz handler) is not in any reference file.

**Fix:** Extend `references/integration-patterns.md` Category 8 (K8s health probe semantics)
with the readiness vs liveness distinction and what a correct /readyz handler checks.

### VE-007 — Mongoose 7 null update behavior
This requires knowing a specific, poorly-documented Mongoose 7 breaking change.
The external-intelligence.md methodology is the correct path (search changelog + GitHub issues)
but the signal (null not persisted) is not strong enough to immediately trigger external search.

**Fix:** Add a pattern to `references/external-intelligence.md`:
"ORM write succeeds (200) but field not updated in DB → check ORM major version changelog
for query transformation behavior changes before assuming application bug."

## Iteration 3 Targets

Based on iteration 2 results, the 3 specific reference file additions that would move
RC-015, RC-018, and VE-007 from 70 to 85+:

1. `frontend-patterns.md` Cat 6: TanStack Query optimistic update pattern
2. `integration-patterns.md` Cat 8: Readiness probe — what /readyz must actually check
3. `external-intelligence.md`: ORM write-but-no-change → check ORM changelog signal

All other 97 cases score 85+. No further additions justified until iteration 3 scoring confirms improvement.
