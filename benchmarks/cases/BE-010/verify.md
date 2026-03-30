# Verification

## Before Fix

Email job consumed → disappears → no delivery, no failure

## After Fix

Email job fails → marked failed in BullMQ → visible in dashboard → retried

## Regression Checks

Test retry limit and dead-letter queue behaviour
