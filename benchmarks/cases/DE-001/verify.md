# Verification

## Before Fix

1. Change code and add a unique sentinel log.
2. Restart with the existing container workflow only.
3. Confirm the sentinel never appears and old behavior remains.

## After Fix

1. Rebuild the image and restart the container from that new build.
2. Re-run the same request.
3. Confirm the sentinel log appears and the fixed behavior is active.

## Regression Checks

- Test repeat rebuilds after future code changes.
- Confirm deployment docs require rebuild, not just restart.
- Confirm version or build metadata is exposed in the running service.

