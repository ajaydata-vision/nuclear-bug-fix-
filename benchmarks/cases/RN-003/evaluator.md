# Evaluator

## Metadata

- id: RN-003
- domain: mobile
- track: bohrbug-core
- difficulty: easy
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: react-native, async-storage, null, first-launch, crash, storage

## Ground Truth

- root_cause: `AsyncStorage.getItem()` returns `null` when the key has never been set. `JSON.parse(null)` coerces `null` to the string `"null"` and returns the JavaScript value `null` without throwing. Accessing `.token` on the resulting `null` throws TypeError. The code does not handle the missing-key case.
- why_it_happens: On first install, the `auth` key has never been written. The API contract for `getItem` is to return `null` for missing keys — correct behavior. `JSON.parse(null)` silently returns `null` (no exception). The crash occurs at `parsed.token` — accessing a property on `null`. The application assumes the key always has a value.
- accepted_fix: Add a null check before `JSON.parse`: `if (!stored) return;` or use optional chaining after parse: `if (parsed?.token)`. Initialize with a loading/guest state rather than crashing.
- rejected_fix_patterns:
  - pre-populate AsyncStorage with an empty auth object at app build time
  - catch the TypeError and silently ignore it
  - use a default value in getItem (AsyncStorage does not support this)

## Evidence Signals

- strongest_signal: Crash only on first install; works after login stores data; crash at `JSON.parse(stored)` where stored came from getItem; error is TypeError not StorageError
- strongest_alternative_explanation: AsyncStorage is not properly initialized or the key name is wrong
- why_alternative_is_wrong: If the key were wrong or AsyncStorage broken, it would also fail after login on reopen — but the code states it works after login, proving AsyncStorage itself works and the key is correct. The issue is purely the missing null guard on first run.

## Scoring Notes

- full_credit_conditions:
  - identifies null return from getItem on missing key as root cause
  - proposes null check before JSON.parse
  - distinguishes this as correct AsyncStorage behavior, not a bug in the library
- partial_credit_conditions:
  - identifies the crash location correctly but suggests try/catch as the only fix
  - recommends initializing storage with a default value without explaining the null guard
- fail_conditions:
  - blames AsyncStorage initialization or library bug
  - suggests checking key name spelling as root fix
  - recommends pre-populating storage at build time
