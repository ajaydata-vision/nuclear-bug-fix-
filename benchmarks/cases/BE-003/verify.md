# Verification

## Before Fix

1. Submit the same semantic create request twice with the same retry token or payload.
2. Confirm two order rows and two email side effects can occur.

## After Fix

1. Replay the same request twice under timeout/retry conditions.
2. Confirm only one order is created.
3. Confirm the second request returns the same semantic result or a safe duplicate response.

## Regression Checks

- Test true new orders still create normally.
- Test retries after partial network failure.
- Test duplicate requests arriving concurrently.

