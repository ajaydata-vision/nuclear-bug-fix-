# Verification

## Before Fix

1. Route repeated requests through the load balancer.
2. Confirm some requests still hit an old-version instance.
3. Confirm only those requests reproduce the old bug.

## After Fix

1. Remove or replace the stale instance.
2. Re-run the same repeated request test.
3. Confirm every instance reports the new version and the old bug no longer appears.

## Regression Checks

- Verify deploy automation checks version on every instance.
- Test rolling restart and scale-up scenarios.
- Confirm health checks do not consider mixed-version pools healthy.

