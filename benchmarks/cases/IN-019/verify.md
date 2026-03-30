# Verification

## Before Fix

429 → immediate retry storm → total service failure

## After Fix

429 → exponential backoff → rate window clears → service recovers

## Regression Checks

Test retry behavior under sustained rate limiting; verify jitter prevents synchronized retries
