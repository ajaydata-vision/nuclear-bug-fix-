# Changelog

## [1.3] - Unreleased

- No unreleased changes yet.

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
