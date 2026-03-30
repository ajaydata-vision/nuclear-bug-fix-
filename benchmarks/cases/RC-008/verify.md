# Verification

## Before Fix

1. Run the full suite in randomized order.
2. Confirm the target test fails intermittently.
3. Run the same test alone and confirm it passes.

## After Fix

1. Re-run the full suite in randomized order.
2. Confirm the target test remains stable.
3. Confirm no test depends on leaked global feature-flag state.

## Regression Checks

- Run the affected package repeatedly in CI-like mode.
- Run with parallel workers and single-worker mode.
- Check other globals, timers, and module caches for similar contamination.

