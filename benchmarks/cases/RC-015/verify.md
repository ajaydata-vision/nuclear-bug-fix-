# Verification

## Before Fix

Rapid likes → optimistic state diverges from server → visible flash

## After Fix

onSettled invalidation → query refetches authoritative count → no persistent desync

## Regression Checks

Test with network throttling (3G) and rapid mutations; verify no flash visible after fix
