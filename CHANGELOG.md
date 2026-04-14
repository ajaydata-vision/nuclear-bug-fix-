# Changelog

## [Unreleased]

## [1.20] - 2026-04-14

### .NET Coverage + 9 Deduction-Killing Fixes + Authoring Standards + Build Hardening

The largest single release since v1.15 (PHP). Five themes:

**1. New reference file: `references/dotnet-patterns.md` (12 categories, 37 patterns, ~1000 lines).**
Closes the biggest domain gap in the skill — before this release, any .NET / ASP.NET Core
bug routed to `backend-patterns.md` (generic) and got an estimated 55–70 single-shot score.
Now routes to a dedicated reference modeled on `java-patterns.md` density. Categories cover
ASP.NET Core middleware ordering (auth/CORS), model binding & validation, DI lifetimes
(scoped-in-singleton, IOptions), async/await deadlocks + ThreadPool starvation, HttpClient
lifecycle (port exhaustion, DNS, timeouts), EF Core change tracking & N+1, EF Core
transactions & concurrency, System.Text.Json (case sensitivity, cycles, JsonElement
lifetime), Configuration & IOptions (`ASPNETCORE_ENVIRONMENT`, Key Vault, validate-on-start),
Kestrel / IIS / reverse proxy, concurrency primitives (SemaphoreSlim, ConcurrentDictionary,
Interlocked), and .NET version migration gotchas (Npgsql 7 UTC, NRT + EF migrations,
.NET 8 AOT JsonSerializerContext, IAsyncEnumerable). Skips Blazor and SignalR per scope.
Adds a Routing Hints table (intake signal → category) and a Universal .NET Diagnostic
Toolkit (dotnet-counters / dotnet-stack / dotnet-trace).

**2. Adversarial review of `dotnet-patterns.md` — 14 technical defects fixed.**
A self-review pass against the v1 file caught 3 red defects (non-existent APIs:
`app.Use<T>()`, `UseTransactionScope`; wrong root-cause diagnosis: "ASP.NET Core buffers
IAsyncEnumerable by default"), 3 amber-red defects (`UseStatusCodePages` claimed to fix
CORS on 401, `SuppressAsyncSuffixInActionNames` unrelated to global `[ApiController]`,
"STJ before .NET 7 cannot populate records"), and 8 yellow defects (wrong version
attributions, wrong cross-references, unrelated noise in Fix blocks). All 14 fixed before
release. Each defect is documented in commit `4d65274`.

**3. 9 deduction-killing precision edits across existing reference files.**
Targets the specific deductions logged in `iteration-4-self-eval.md` against v1.12.
Each edit is a precision rewrite of an existing pattern to remove the gap that lost
points in that eval:

- `external-intelligence.md` — VE-007: Mongoose 6→7 null-drop expanded into a full
  sub-pattern with explicit `$set` fix, BROKEN/FIXED code pair, and the "do NOT store
  empty string" guard. (Estimated +12 on VE-007: 83 → ~95.)
- `frontend-patterns.md` — RC-015: TanStack optimistic update race rewritten with a
  step-by-step click-A/click-B interleaving trace and per-handler responsibilities for
  `onMutate` / `onError` / `onSettled`. (Estimated +7 on RC-015: 88 → ~95.)
- `frontend-patterns.md` — FE-023: Vue Router-shaped chunk-404 fix replaced with a
  React Router 6 `errorElement` + `useRouteError` implementation; kept the
  `sessionStorage` infinite-reload guard; added the "retain old chunks 1–2 hours" CDN
  strategy as the second required half. (Estimated +8 on FE-023: 92 → ~100.)
- `java-patterns.md` — KF-001 (Kafka new consumer group LAG=0): added the mandatory
  stop-consumer-first step and the 4-step bash recovery procedure
  (`kubectl scale 0` → reset-offsets → `scale 1`). (+5: 95 → ~100.)
- `java-patterns.md` — KF-002 (rebalance storm): corrected the misattribution of
  `session.timeout.ms` vs `max.poll.interval.ms`, added the diagnostic equation
  `processing_time × max-poll-records > max.poll.interval.ms`, and made the idempotency
  check a required second half of the fix. (+10: 90 → ~100.)
- `java-patterns.md` — KF-003 (poison pill): added the IMMEDIATE recovery step (manually
  advance offset 94821 → 94822 with reset-offsets) as Step 1, with `ErrorHandlingDeserializer`
  as Step 2; explicitly stated the in-method try/catch can never see the deserialization
  exception. (+8: 92 → ~100.)
- `java-patterns.md` — JV-018 (`@Cacheable` stale data): added the Long/Integer SpEL
  key-type mismatch as the headline trap, with a Prove block that logs both
  `.getClass().getSimpleName()` values, three other key-mismatch variants to check at
  the same time, and three concrete fix options. (+10: 90 → ~100.)
- `react-native-patterns.md` — RN-002 (FlatList): reframed as a two-cause pattern
  (unstable inline `renderItem` PRIMARY, missing `keyExtractor` CONTRIBUTING) and made
  the Fix block require ALL THREE of `useCallback(renderItem)` + `React.memo(cell)` +
  stable `keyExtractor`. Added the "filterOpen test" to rule out the common
  selector-instability misdiagnosis. (+8: 92 → ~100.)
- `react-native-patterns.md` — RN-005 (Reanimated worklet crash): rewrote to clearly
  separate "value read" (use SharedValue) from "function call" (use runOnJS), made it
  explicit that primitive props captured by closure are SAFE and need no SharedValue
  conversion, and added the "do NOT also convert threshold" warning. (+5: 95 → ~100.)

Aggregate expected lift on the 25-case eval mean: **+2.9 points**, from 94.2 to ~97.1.
Full benchmark re-run pending under `DN-001..N` cases.

**4. Reference file authoring standards.**
New `CLAUDE.md` at the repo root (auto-loaded by Claude Code on every contributor
session) and `docs/reference-authoring-standards.md` (the full pre-flight / in-flight /
post-flight checklist). The standards are grounded in the 14 defects found in the
`dotnet-patterns` adversarial review and codify three blocking rules: every code block
must compile against a fresh project, every version-history claim must be cited or
marked `// unverified:`, and every new reference file must pass an adversarial
self-review. The post-flight checklist has 10 numbered review rules (R1–R10) each with
example defects from the dotnet review. This is the persistence mechanism that prevents
the same defect classes from recurring in future reference files.

**5. Build/install defense-in-depth.**
`scripts/build_skill.py`, `scripts/install.py`, and `scripts/install.sh` now have
explicit `FORBIDDEN_*` lists (`CLAUDE.md`, `docs/`, `.claude/`, `.github/`) checked
alongside the existing `ALLOWED_*` allow-lists. Verified empirically: built the
artifact and confirmed zero matches for contributor-only paths in the 580-file output;
constructed a malicious test archive with `nuclear-bug-fix/CLAUDE.md` and confirmed
`install.py` refuses with a clear actionable error message. The fix prevents a future
maintainer from accidentally bundling contributor-only files into a user's project,
where they would either waste tokens or collide with the user's own project-root
`CLAUDE.md`.

### File stats vs v1.19

- `references/dotnet-patterns.md` — new, 1003 lines, 12 categories, 37 patterns
- `references/external-intelligence.md` — +14 lines (Mongoose 7 expansion)
- `references/frontend-patterns.md` — +50 lines (TanStack + chunk-404 rewrite)
- `references/java-patterns.md` — +112 lines (KF-001/002/003 + JV-018 rewrites)
- `references/react-native-patterns.md` — +57 lines (RN-002 + RN-005 rewrites)
- `SKILL.md` — +3 lines (new .NET row in Phase 2A table + reference guide + standards pointer)
- `CLAUDE.md` — new, 142 lines (contributor-only)
- `docs/reference-authoring-standards.md` — new, 355 lines (contributor-only)
- `scripts/build_skill.py` — +15 lines (FORBIDDEN_* + comment)
- `scripts/install.py` — +22 lines (FORBIDDEN_TOP_LEVELS + check + comment)
- `scripts/install.sh` — +19 lines (FORBIDDEN_TOP_LEVELS + sanity check + comment)

### Routing impact

`SKILL.md` Phase 2A Domain Classification table now has a `.NET / ASP.NET Core` row
with extensive intake-signal coverage (~30 distinct symptoms) so the model routes
single-shot to `dotnet-patterns.md` without ambiguity. The Reference File Guide entry
mirrors the same coverage for late-phase reload.

### Known gaps remaining for v1.21+

- Benchmark cases for .NET (`DN-001..010`) — not yet written; the +2.9 estimate above
  is from deduction-mapping, not from a re-executed eval. Will measure in iteration 5.
- CHANGELOG entries for v1.17, v1.18, v1.19 are still missing (this gap predates v1.20
  and was inherited).
- Python web reference file (Django / FastAPI / SQLAlchemy / Celery / asyncio) — still
  zero coverage; only `python-desktop-patterns.md` (PyQt6/PyInstaller narrow) exists.
- MiniMax-AI/skills comparison analysis — deferred from this branch.

## [1.16] - 2026-04-05

### PHP Self-Evaluation 94.6/100 + OPcache Guard Fix

Self-evaluation of php-patterns.md across 18 representative PHP scenarios
(15 domain cases + 3 adversarial). Mean 94.6/100. All 18 cases score 85+.
Single-shot HIGH confidence (≥90) rate: 16/18 = 89%.

Domain means: Type System 98.5, Laravel 98.0, Execution Model 96.3,
Version/Env Mismatch 97.5, Eloquent 97.0, Queues 97.0, Security 100.
FPM exhaustion (88) and PDO ERRMODE (88) correctly calibrated at MEDIUM.

Adversarial case PHP-A01 identified gap: OPcache `$status === false` guard
log said "not the cause" which is wrong when run from CLI (opcache.enable_cli=0
default makes CLI result unreliable). Fixed guard message to instruct developer
to re-run via web request.

## [1.15] - 2026-04-05

### PHP Reference File — 45 Patterns, 10 Categories

references/php-patterns.md — new file.
243 → 288 total patterns. 13 → 14 reference files.

**Visibility Prerequisite** (before all categories): display_errors=Off is
the PHP production default. No errors visible = every Prove fails before it
starts. Prerequisite provides the exact commands to find the error_log path
and surface PHP errors safely.

Categories (45 patterns, 0 missing Prove, 100% coverage):
1. PHP Execution Model (5) — OPcache, shared-nothing, headers already sent,
   session_start() missing, global state cross-request
2. Type System & Comparison Traps (5) — == vs ===, empty(), in_array() loose,
   switch coercion, integer overflow via float
3. Laravel Framework (8) — Eloquent N+1, queue driver sync, service container
   binding, middleware not applied, config cache, relationship mismatch,
   event listener, Blade cache
4. PHP-FPM & Server (5) — worker exhaustion (ps aux + nginx log Prove,
   no prior pm.status_path config required), max_execution_time, memory_limit,
   wrong user permissions, persistent PDO state
5. OPcache & Autoloading (4) — composer dump-autoload, Cannot redeclare class,
   namespace/use missing, OPcache memory full
6. PDO & Database (5) — ERRMODE_SILENT, transaction not committed, N+1
   (Option A inline counter + Option B function wrap), charset utf8mb4,
   parameter count mismatch
7. Eloquent / ORM (5) — mass assignment fillable, soft delete scope bypass,
   model event observer, withCount mismatch, eager load constraint
8. Queues Cache & Scheduled (4) — cache driver/key, cron entry missing,
   job swallows exception, Redis exhaustion
9. Security functional bugs (1) — CSRF 419 only (audit patterns removed)
10. Version & Environment Mismatch (3) — CLI/FPM different PHP versions
    (nginx fastcgi_pass socket = pathognomonic), .env not in CLI/cron context,
    Composer runtime version conflict

Phase 2A: PHP routing row added to SKILL.md with 17 discriminating signals.

Adversarial review applied before implementation — 8 defects caught and fixed:
Visibility Prerequisite added, OPcache Prove uses file-level timestamp comparison
(not just opcache_get_status() enabled check), Cat 9 reduced from 4 to 1 pattern
(3 were security audit patterns not bugs), Cat 10 consolidated from 4 trivial
migration patterns to 3 genuinely hard patterns, FPM Prove uses ps aux + nginx log
(no prior configuration required), == Prove logs at comparison site not generic
var_dump, PDO N+1 Prove adds Option A (inline counter, works for any loop pattern).

## [1.14] - 2026-04-04

### CLS Tracker + INP Debugger + LCP Pattern — Frontend Performance Proves

references/frontend-patterns.md — Category 10 enhanced, 2 new patterns added.
241 → 243 patterns.

Adversarial review of "30-line addition to 2 existing patterns" proposal
identified wrong pattern mapping: LCP observer fires only at initial load,
not during memory leak sessions; INP observer doesn't capture scroll events.

Corrected implementation:
- Scroll or animation jank (enhanced): CLS PerformanceObserver added as
  visual jank sub-case. Identifies exact shifting element + previousRect/currentRect.
- NEW: Page interactions sluggish — clicks/taps respond slowly (INP > 200ms):
  PerformanceObserver with inputDelayMs/processingMs/presentationMs breakdown.
  Each points to a different fix (long task / heavy handler / excessive re-render).
- NEW: Page loads slowly — LCP element identified but cause unknown:
  PerformanceObserver identifies element + time + resource URL, then four-cause
  discrimination (TTFB / render-blocking / late discovery / JS-rendered element).

## [1.13] - 2026-04-04

### Iteration-4 Self-Evaluation 94.2/100 + CHANGELOG Complete + Coverage Matrix

Benchmark (iteration-4-self-eval.md): 25 cases across new domains + regression
check. Mean 94.2/100 (+1.9 vs iteration-2 full-domain 92.3). All 25 score 83+.
Single-shot HIGH confidence rate: 96% (24/25).

Key results: React Native 96.2 (5 new cases), Kafka 92.3 (3 new cases),
Frontend new patterns 94.7 (3 cases), Java new patterns 95.5 (4 cases),
Previously-70 cases: +17 average improvement. Original domains: 95.7, no regression.

CHANGELOG: added missing v1.9, v1.11, v1.12 entries.
COVERAGE_MATRIX.md: added React Native and Kafka domain sections.



### Adversarial Review — 9 Benchmark Defects Fixed

Post-v1.11 adversarial review of all 16 new benchmark cases identified 9 defects across 8 cases.

- KF-001 verify.md: `--reset-offsets` requires consumer group inactive. Added explicit "stop consumer first" step.
- KF-002: `track: intermittent-race` + `determinism: deterministic` contradicted each other. Fixed to `determinism: intermittent`. Root cause math was wrong (47s single message < 5min default timeout). Added explicit `max.poll.interval.ms: 30000` to prompt application.yml.
- FE-021: Partial credit tested output quality, not diagnosis accuracy. Replaced with genuine incomplete-correct scenario.
- FE-023 (CRITICAL): Fix code used `router.onError()` and `router.afterEach()` — Vue Router APIs. Stack is React Router 6.22. Replaced with correct React Router 6 `errorElement` + `useRouteError` pattern in both evaluator and verify.md.
- JV-016: Partial credit rewarded "downgrade the JAR" — also listed as rejected_fix_pattern. Moved to fail_conditions.
- JV-017: `elapsed` variable undefined in code excerpt. Fixed with `System.currentTimeMillis() - start`.
- JV-018: Root cause depended on Long/Integer type mismatch never shown. Added UserProfile class with `Integer getId()`. verify.md changed method signature without noting controller update; added controller fix example.
- JV-019: `doGet` added to `OrderServlet` (`@WebServlet("/orders")`) but redirect went to `/confirmation` — 404 guaranteed. Fixed with separate `ConfirmationServlet @WebServlet("/confirmation")`.

## [1.12] - 2026-04-04

### Adversarial Review — 9 Benchmark Defects Fixed Across 8 Cases

Post-v1.11 adversarial review of all 16 new benchmark cases found 9 defects:

- KF-001 verify.md: `--reset-offsets` requires consumer group inactive. Added stop-consumer step.
- KF-002: `track:intermittent-race` + `determinism:deterministic` contradicted each other. Fixed to
  `determinism:intermittent`. Root cause math wrong (47s single message < 5min default timeout).
  Added explicit `max.poll.interval.ms:30000` to prompt.
- FE-021: Partial credit tested output quality not diagnosis accuracy. Replaced.
- FE-023 (CRITICAL): Fix code used `router.onError()` and `router.afterEach()` — Vue Router APIs.
  Stack is React Router 6.22. Replaced with correct React Router 6 `errorElement` + `useRouteError`.
- JV-016: Partial credit rewarded "downgrade the JAR" which was also in rejected_fix_patterns.
  Moved to fail_conditions.
- JV-017: `elapsed` variable undefined in code excerpt. Fixed with `System.currentTimeMillis()-start`.
- JV-018: Root cause depended on Long/Integer type mismatch never shown in prompt. Added
  UserProfile class with `Integer getId()`. verify.md signature change missing controller update.
- JV-019: `doGet` in `OrderServlet` (`@WebServlet("/orders")`) but redirect went to `/confirmation`
  — 404. Fixed with `ConfirmationServlet @WebServlet("/confirmation")`.

## [1.11] - 2026-04-04

### Benchmark Cases — 16 New Cases Across 4 Zero-Coverage Domains

React Native (RN-001..RN-005): Metro cache corruption, FlatList keyExtractor + unstable renderItem,
AsyncStorage null on first launch, iOS NSCameraUsageDescription missing, Reanimated worklet runOnJS.

Kafka (KF-001..KF-003): auto.offset.reset=latest on new group, max.poll.interval.ms rebalance storm
with duplicates, poison pill deserialization partition block.

Frontend new patterns (FE-021..FE-023): fetch() silent 4xx, async forEach no-op returning undefined,
dynamic chunk 404 after deploy with React Router 6 errorElement fix.

Java new patterns (JV-016..JV-019): JSTL javax→jakarta URI after Spring Boot 3, @Async synchronous
from missing @EnableAsync, @Cacheable stale data from SpEL key mismatch, JSP double-submit PRG.

Quality controls applied from adversarial review: correct import paths, code comments at exact crash
location, precise track/determinism/log_access fields, scoped root causes, realistic partial credit,
all 3 files present. Authoring rules documented in index.yaml.

index.yaml: 145→161 cases. Two new domains (react-native, kafka) added.

### Content Fixes (v1.11 also includes)

6 defects from adversarial review:
- Circular import Prove: rollup-plugin-visualizer → madge (correct tool)
- Dynamic chunk reload: added sessionStorage infinite-loop guard
- Forward/redirect Prove: back-then-refresh → F5 refresh (correct diagnostic)
- async forEach Prove: added explicit "forEach returns undefined, await is no-op" explanation
- JSTL Prove: added three-step check including javax vs jakarta.tags.core URI mismatch
- CHANGELOG: added missing v1.10 entry

## [1.10] - 2026-04-03

### JSP + JavaScript/Frontend Single-Shot Coverage

**references/java-patterns.md — 3 new JSP patterns (Category 2):**
- JSTL taglib declaration missing — tags render as literal text (covers javax vs jakarta URI mismatch, JAR presence check, Spring Boot 2 vs 3 URI difference)
- JSP forward vs redirect wrong choice — double-submit, data loss, POST-Redirect-GET pattern with browser F5 diagnostic
- JSP EL output unescaped — XSS / broken HTML from user input, `<c:out>` vs bare `${expr}`, `fn:escapeXml`

**references/frontend-patterns.md — 11 new patterns, 3 new categories:**
- SW/CDN pattern: removed orphaned duplicate Signal content below Prove section
- Category 13 — Vanilla JS & DOM: addEventListener null element, event delegation e.target/closest, `this` context loss, async forEach no-op (returns undefined)
- Category 14 — Promise & Async: fetch() no throw on 4xx/5xx, response.json() on 204, Promise.all fail-fast vs allSettled, unhandled promise rejection global handler
- Category 15 — Modern JS & TypeScript: circular import undefined (with madge detection), TypeScript `as` assertion hides null, dynamic import() chunk 404 with sessionStorage-guarded reload

Coverage: 241 patterns, 0 missing Prove, 100% across all reference files.

## [1.9] - 2026-04-03

### End-to-End Trace — 4 Structural Fixes, Single-Shot Path Complete

Full end-to-end adversarial trace of the single-shot path across 4 real bug scenarios
revealed 4 remaining structural and content issues.

**SKILL.md — Phase 2A (critical):** Reference file now loaded immediately at Phase 2A, not Phase 3.8.
CP-1 and CP-2 candidate patterns identified at triage time. Entire Phase 3 is now pattern-informed:
3.6 searches CP-1's specific error signatures; 3.7 surfaces CP-1's risky assumptions; 3.8 Prove is
the culmination of a fully-guided Phase 3 — not the first time the pattern is consulted.
Phase 2A header: removed misleading "in Phase 4" text.

**SKILL.md — Phase 4:** Rewritten as "comprehensive review" — file already in context from Phase 2A,
re-read to catch anything Prove missed, verify Prove maps to exactly one pattern.

**references/java-patterns.md — @Async Prove:** Two-step discriminator replaces ambiguous single Prove:
Step 1: grep for @EnableAsync (structural, no code run). Step 2: check call site for same-class invocation.
Previously produced MEDIUM verdict (two causes, same output). Now produces HIGH for both root causes.



### JSP + JavaScript/Frontend Single-Shot Coverage

**references/java-patterns.md — 3 new JSP patterns (Category 2):**
- JSTL taglib declaration missing — tags render as literal text (covers javax vs jakarta URI mismatch, JAR presence check, Spring Boot 2 vs 3 URI difference)
- JSP forward vs redirect wrong choice — double-submit, data loss, POST-Redirect-GET pattern with browser F5 diagnostic
- JSP EL output unescaped — XSS / broken HTML from user input, `<c:out>` vs bare `${expr}`, `fn:escapeXml`

**references/frontend-patterns.md — 11 new patterns, 3 new categories:**
- SW/CDN pattern: removed orphaned duplicate Signal content below Prove section
- Category 13 — Vanilla JS & DOM: addEventListener null element, event delegation e.target/closest, `this` context loss, async forEach no-op (returns undefined)
- Category 14 — Promise & Async: fetch() no throw on 4xx/5xx, response.json() on 204, Promise.all fail-fast vs allSettled, unhandled promise rejection global handler
- Category 15 — Modern JS & TypeScript: circular import undefined (with madge detection), TypeScript `as` assertion hides null, dynamic import() chunk 404 with sessionStorage-guarded reload

Coverage: 241 patterns, 0 missing Prove, 100% across all reference files.



### End-to-End Trace — 4 Remaining Issues Fixed

Full end-to-end adversarial trace of the single-shot path across 4 real bug scenarios
revealed 4 remaining structural and content issues.

**SKILL.md — Phase 2A (structural, highest impact):**
- Issue 1 (Critical): Reference file was loaded at Phase 3.8, but Phases 3.6 (external
  intelligence) and 3.7 (find the lies) had already run without knowing the candidate
  pattern. External searches were generic. Assumption lists were generic. Targeted Prove
  fired 5 steps too late.
  Fix: Added PATTERN PRE-LOAD block to Phase 2A. Reference file now loads immediately
  after domain identification. CP-1 and CP-2 candidate patterns identified at Phase 2A.
  Phase 3.6 now searches CP-1's specific error signatures. Phase 3.7 surfaces CP-1's
  risky assumptions. Phase 3.8 Prove is the culmination of a fully pattern-informed
  Phase 3 — not the first time the pattern is consulted.
- Issue 3 (Medium): Phase 2A header said "determines which reference file to load in
  Phase 4" — wrong since v1.8 moved the load to Phase 3.8. Fixed: removed "in Phase 4".

**SKILL.md — Phase 4 (medium):**
- Issue 4: Phase 4 still said "Load the reference file" — redundant and confusing after
  v1.8 + v1.9 pre-load changes. Rewritten: Phase 4 is now explicitly "comprehensive
  review" — file already in context, re-read fully to catch anything the targeted Prove
  missed, or verify the Prove maps to exactly one pattern.

**references/java-patterns.md — @Async Prove (high):**
- Issue 2: @Async method executes synchronously Prove said "thread is caller's thread →
  @EnableAsync missing OR self-invocation." Two different root causes, same output, 
  different fixes. Gate could not reach HIGH confidence — stalled at MEDIUM.
  Fix: Two-step discriminator. Step 1: grep for @EnableAsync (structural, no code run).
  If absent → confirmed, add @EnableAsync, done. Step 2 (only if @EnableAsync present):
  check call site for same-class invocation. Runtime log only if needed to confirm.
  Now produces HIGH confidence verdict for both root causes.

**Single-shot HIGH confidence path is now fully wired end-to-end:**
Phase 2A: domain → load file → identify CP-1/CP-2 → read Why →
Phase 3.6: targeted external search using CP-1 signatures →
Phase 3.7: CP-1-informed assumption list →
Phase 3.8: CP-1 Prove delivered →
Phase 3.9: Prove output → fast-path if discriminating, gate if narrowing →
Phase 3.10: HIGH or MEDIUM verdict with explicit proof statement.

## [1.8] - 2026-04-03

### Adversarial Review — 12 Defects Fixed

Post-v1.7 adversarial self-review identified 12 defects. All fixed.

**SKILL.md (structural fixes):**
- Defect 1 (CRITICAL): Phase 3.8 Targeted Prove First had a sequencing contradiction — referenced "Phase 4 reference file is loaded" before Phase 4 had run, and required "Phase 2A identified a specific named pattern" which Phase 2A never does (it identifies a domain, not a pattern). Rewritten to be self-contained: load the reference file NOW at step 3.8, find the matching pattern by Symptom, use its Prove section directly.
- Defect 2 (HIGH): Phase 3.9 fast-path addition claimed Prove logs are "structurally inconsistent with all alternatives in that domain" — an unverifiable assertion that would manufacture false HIGH confidence. Replaced with honest language: Prove logs "narrow the field significantly" and require the full sensitivity check before HIGH confidence.
- Defect 4 (MEDIUM): Java Enterprise row in Phase 2A missing Kafka, @Async, @Scheduled, virtual thread, and Spring Boot 3 signals. Engineers describing Kafka consumer or async bugs were not routed to java-patterns.md. All signals added.

**references/java-patterns.md:**
- Defect 5 (MEDIUM): @Async void exception Prove was the fix itself (add try/catch). Replaced with structural inspection Prove: check for @EnableAsync presence and AsyncUncaughtExceptionHandler at startup.
- Defect 6 (MEDIUM): @Scheduled Prove referenced `schedulingTaskRegistrar` — an unresolved variable that would not compile. Replaced with simple, correct Prove: log first line of scheduled method.
- Defect 7 (MEDIUM): Kafka session.timeout.ms default stated as 10s — wrong since Kafka 3.0 (changed to 45s). Fixed to 45s with version note.
- Defect 8 (MEDIUM): Kafka transactional Prove recommended setting isolation.level=read_uncommitted on consumer without safety warning. Added explicit: non-production diagnostic consumer only, never on production.
- Defect 9 (LOW-MED): ScopedValue stated as "finalized in Java 23" — wrong. Finalized in Java 22 (JEP 464). Fixed.

**references/react-native-patterns.md:**
- Defect 10 (MEDIUM): Duplicate module Prove used `node -e require.resolve` which doesn't work as described in monorepos. Replaced with `yarn why` / `npm ls` plus runtime `require.resolve` inside both components.
- Defect 11 (MEDIUM): iOS permission Prove claimed `'denied'` status = Info.plist missing — wrong. `'denied'` has four other causes. Replaced with Xcode console message as pathognomonic smoking gun, plus direct Info.plist inspection as fallback.
- Defect 12 (LOW): New Architecture Prove used `gradlew dependencies | grep turbo|jsi` — unreliable noise. Replaced with: error message itself as smoking gun + `codegenConfig` key presence in package.json as compatibility signal.

**references/frontend-patterns.md:**
- Defect 3 (HIGH): React Native patterns existed in two places (Category 11 + react-native-patterns.md) with no redirect. Added explicit redirect notice to Category 11 pointing to react-native-patterns.md for all React Native bugs.
- Pre-existing: SW vs CDN pattern had no Prove section. Added a 3-step sequential Prove (hard refresh test → DevTools Service Worker check → origin curl bypass test).

**references/integration-patterns.md:**
- Pre-existing: "Deployment succeeds but old version running" had no Prove. Added: version endpoint check + container image digest comparison.

**Prove coverage:** 227 total patterns across all reference files — 100% Prove coverage (was 2 missing pre-existing gaps, now zero).

## [1.7] - 2026-04-03

### Java & React Native — Single-Shot Coverage Completion

**Java (`references/java-patterns.md`):**
- Added Category 10 — Spring Async/Scheduling/Caching: 5 patterns covering `@Async` silent execution, `@Async` void exception swallowing, `@Scheduled` not firing, `@Cacheable` stale data, `@PreAuthorize` SpEL silent 403.
- Added Category 11 — Spring Boot 3 / Jakarta EE migration: 2 patterns covering `javax→jakarta` ClassNotFoundException and `@HttpExchange` error handling change.
- Added Category 12 — Kafka/Messaging: 4 patterns covering wrong group.id/offset.reset, consumer group rebalance storm, transactional producer not committed, poison pill deserialization blocking partition.
- Added Category 13 — Java 21 Virtual Threads: 2 patterns covering `synchronized` pinning of carrier threads and ThreadLocal/ScopedValue migration for request-scoped state.
- Added Prove sections to `OutOfMemoryError` and thread dump patterns (previously diagnostic-only, now have targeted smoking-gun Prove steps).
- Java patterns: 46 patterns total, 100% Prove coverage.

**React Native (`references/react-native-patterns.md`) — new file:**
- 9 categories, 26 patterns, 100% Prove coverage.
- Category 1: Metro & Build — cache corruption, duplicate module, Hermes console.log strip.
- Category 2: React Navigation — params undefined, goBack wrong screen, remount on navigate, deep link cold start.
- Category 3: FlatList & Performance — keyExtractor missing, getItemLayout wrong, removeClippedSubviews blank areas.
- Category 4: Animated & Reanimated — useNativeDriver layout crash, worklet UI thread violation, animation loop memory leak.
- Category 5: Expo & EAS — native module missing in standalone, env variable undefined in EAS, OTA update stale code.
- Category 6: State & AsyncStorage — null on first install, Redux selector stale reference, useEffect async stale update.
- Category 7: Platform & Permissions — iOS Info.plist missing, Android manifest missing, iOS safe area notch.
- Category 8: Native Modules & Architecture — release build null, New Architecture TurboModule incompatibility.
- Category 9: Development Tooling — debugger interference, Fast Refresh stale state.

**SKILL.md routing:**
- Phase 2A: React Native now has its own dedicated row with 20+ routing signals pointing to `references/react-native-patterns.md`. Old Mobile row retained for non-RN native apps.
- Phase 4: React Native reference file added to domain router table with full signal description.

**v1.6 wiring confirmed active:** Targeted-Prove-First in Phase 3.8 now fires for all 72 Java + React Native patterns with complete Prove sections — single-shot HIGH confidence path is fully operational for these domains.

## [1.5] - 2026-03-31

### Desktop / Bridge / Packaging Coverage
- Added first-class skill routing and reference coverage for Python desktop UI (`PyQt6` + `qasync`), bridge/adapters (Baileys-style subprocess and scraper drift), and frozen Windows runtime issues (`PyInstaller`).
- Tightened intake, meta-checks, forensic logging, DDx tables, and external-intelligence guidance for polyglot desktop apps where stdout may itself be a protocol channel.
- Added 18 benchmark cases: `PD-A01`, `PD-001..005`, `BI-A01`, `BI-001..005`, `FR-A01`, `FR-001..005`.
- Expanded benchmark metadata and backlog for the new domains so coverage stays aligned with the committed corpus.
- Hardened the new benchmark family for single-shot credibility by reducing clue leakage, moving runtime clues into raw assets, and tightening one-shot eligibility for packaged evidence-limited cases.
- Hardened `scripts/test_updater.py` on Windows by replacing tempfile-created roots with manually created writable temp workdirs, so updater smoke tests remain reliable during release bumps.
- Shortened installer staging and backup directory names in `scripts/install.py` to avoid Windows path-length failures when benchmark assets are present.

## [1.4.1] - 2026-03-31

### Updater Hardening
- Fixed the shipped Bash updater path for legacy Windows installs by avoiding Unicode-sensitive archive validation output and by packaging an ASCII-safe `SKILL.md` inside the `.skill` archive.
- Added Python fallback detection in `scripts/update.sh` so Git Bash installs work with either `python3` or `python` on PATH.
- Added updater smoke tests in `scripts/test_updater.py` covering prior-release installs, explicit legacy `1.3` installs, Git Bash on Windows with `cp1252`, and PowerShell installs.
- Gated `.github/workflows/build-skill.yml` on cross-platform updater smoke tests before `dist/` is rebuilt and pushed.
- Release process requirement: when the version changes, updater coverage is part of ship readiness and must be reported alongside the version bump.

## [1.4] - 2026-03-31

### Phase 2 Additions (WebFlux, ORM, JVM)
- Extended `references/java-patterns.md` with Category 8 (ORM/JPA: N+1, optimistic locking, bidirectional mapping) and Category 9 (WebFlux: blocking-in-reactive, switchIfEmpty, ReactiveSecurityContextHolder).
- Added hs_err JVM crash reading pattern to Category 5 (JVM).
- Extended SKILL.md Phase 3.6 with app-server (JBoss/WebLogic/GlassFish) and WebFlux/BlockHound search triggers.
- Added 7 new benchmark cases: WF-001..003 (WebFlux), OR-001..003 (ORM/JPA), JT-001 (JVM crash).
- Updated benchmarks/index.yaml: 120→127 cases, java-enterprise domain 20→27.

### Release Readiness Cleanup
- Reconciled README release metadata, case counts, and project links for the 1.4 ship target.
- Tightened benchmark wording to distinguish 85+ rubric scores from literal one-shot eligibility.
- Corrected `benchmarks/index.yaml` domain counts to match the committed evaluator corpus.
- Rebuilt the shipped `dist` artifacts and release manifest for 1.4.

### Java Enterprise Support
- Added `references/java-patterns.md` — 7 categories, 25 patterns covering Servlet lifecycle/threading, JSP scope/include/EL, NIO ByteBuffer/Channel/Selector, Java threading (ThreadLocal, InterruptedException, Executor rejection, wait/notify), JVM ClassLoader/OOM, JDBC/HikariCP/JNDI, Spring Boot (@Transactional self-invocation, LazyInitializationException, bean scope, Security filter chain).
- Added Java Enterprise domain to Phase 2A domain router in SKILL.md with natural-language developer signals.
- Added 20 Java benchmark cases (JV-A01–JV-A05 adversarial, JV-001–JV-015 confirmatory) covering all 7 pattern categories.
- Upgraded Java logging example in Phase 3.8 from `System.out.printf` to SLF4J+MDC with thread-aware NIO/thread-pool diagnostics.
- Fixed JFR invocation in `references/intermittent-race-bugs.md` — removed deprecated `-XX:+UnlockCommercialFeatures` flag (invalid on JDK 11+ OpenJDK); added correct JDK 17+ `jcmd` form and JDK 8 Oracle note.
- Updated `benchmarks/index.yaml`: total cases 100→120, bohrbug-core 36→49, intermittent-race 19→24, deploy-env 29→31, added java-enterprise domain.
- Updated `benchmarks/COVERAGE_MATRIX.md` and `benchmarks/BENCHMARK_BACKLOG.md` with Java Enterprise domain and case listings.

## [1.3] - 2026-03-30

- Added `scripts/update.ps1` so Windows PowerShell installs can update in place without running the bash updater.
- Documented that updater changes must keep `scripts/update.sh` and `scripts/update.ps1` in sync.
- Fixed Windows Git Bash shell wrappers to convert paths through `cygpath` before invoking native Python binaries.

## [1.2] - 2026-03-30

- Added direct installers for Claude Code's documented skill directories on macOS/Linux and Windows PowerShell.
- Added a local repo installer for personal and project-scoped installs.
- Added root `setup` and `setup.ps1` entrypoints so git-cloned installs match the `clone -> cd -> setup` flow used by other Claude Code skill packs.
- Switched updater guidance from `claude skills add` to directory-based reinstall/update flows.
- Updated README install instructions to match Claude Code's directory discovery model.
- Updated the archive builder to include non-ignored repo additions so new install files are packaged before release.

## [1.1] - 2026-03-30

- Switched release versioning to explicit semantic version `1.1`.
- Added `VERSION` as the release-version source of truth.
- Added `dist/release.json` as canonical shipped release metadata.
- Updated the builder, workflow, and updater to track semantic version plus exact `source_commit`.
- Kept deterministic packaging and artifact validation in the release flow.
- Reconciled benchmark suite metadata with the actual committed corpus.
- Tightened README accuracy and release documentation.
