# Verification

## Before Fix

Cache expiry → hundreds of simultaneous DB queries → database overload

## After Fix

Cache expiry → one refresher with lock → others wait → single DB query

## Regression Checks

Load test during cache expiry window; verify DB query count drops to 1
