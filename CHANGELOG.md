# Changelog

## [Unreleased]

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
