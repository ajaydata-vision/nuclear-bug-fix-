# Verification

## Before Fix

1. Simulate two overlapping searches with different response times.
2. Confirm an older response can overwrite a newer one.
3. Confirm the UI ends empty or stale.

## After Fix

1. Repeat the same rapid typing sequence.
2. Confirm only the latest request can update the UI.
3. Confirm stale or aborted requests do not overwrite results.

## Regression Checks

- Test with fast network and intentionally delayed network.
- Test empty-result searches that are actually current.
- Test component unmount during an in-flight request.

