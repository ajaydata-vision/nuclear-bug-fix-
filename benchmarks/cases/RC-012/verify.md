# Verification

## Before Fix

3 workers → all claim same subscription → 3 charges

## After Fix

3 workers → only 1 claims with SKIP LOCKED → 1 charge

## Regression Checks

Verify no subscription can be charged twice; test with 10 concurrent workers
