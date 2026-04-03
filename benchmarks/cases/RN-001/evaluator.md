# Evaluator

## Metadata

- id: RN-001
- domain: mobile
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, metro, bundler, cache, file-rename, expo

## Ground Truth

- root_cause: Metro's persistent file map cache still contains the old filename mapping. After a file rename, Metro resolves modules from its stale cache and fails to find the new path even though the file exists on disk.
- why_it_happens: Metro maintains a persistent cache of the module graph across restarts for performance. A file rename invalidates the module's identity in that graph, but the cache is not automatically cleared. Metro looks up `UserProfile` in the cache, finds no entry (the old entry was for `UserCard`), and reports the module as unresolvable.
- accepted_fix: Run `npx react-native start --reset-cache` or `npx expo start --clear` to wipe Metro's persistent cache. The error disappears on the next start without any code change.
- rejected_fix_patterns:
  - delete and reinstall node_modules (does not clear Metro cache)
  - revert the file rename and use the old name
  - add explicit path resolution in metro.config.js
  - check for case-sensitivity issues (file exists, case is correct)

## Evidence Signals

- strongest_signal: Error persists after `node_modules` reinstall; file exists at the exact path Metro reports as missing; issue started immediately after a file rename with no other changes
- strongest_alternative_explanation: Case-sensitive filesystem mismatch (macOS case-insensitive, Linux CI case-sensitive)
- why_alternative_is_wrong: The file path and import are identical character-for-character; the error reproduces on the same macOS machine where the rename was done, ruling out cross-platform case sensitivity

## Scoring Notes

- full_credit_conditions:
  - identifies Metro cache as root cause
  - prescribes --reset-cache or --clear flag, OR manually deleting the .metro cache directory (both are valid)
  - explains why node_modules reinstall does not fix Metro cache
- partial_credit_conditions:
  - mentions cache without specifically naming Metro's persistent file map
  - identifies cache as cause but cannot name the correct flag
- fail_conditions:
  - blames the import statement or file path
  - suggests case-sensitivity as root cause
  - recommends changing metro.config.js resolver
