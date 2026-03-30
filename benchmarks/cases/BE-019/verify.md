# Verification

## Before Fix

Update → GET returns stale for 1 hour

## After Fix

Update → cache invalidated → GET returns fresh data immediately

## Regression Checks

Test cache invalidation on delete operations too
