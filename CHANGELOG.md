# Changelog

## [1.4] - Unreleased

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
