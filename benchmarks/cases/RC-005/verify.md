# Verification

## Before Fix

Update → WS broadcast → HTTP response (race on fast networks)

## After Fix

Update → HTTP response → WS broadcast (ordered correctly)

## Regression Checks

Test concurrent updates from multiple clients for conflict detection
