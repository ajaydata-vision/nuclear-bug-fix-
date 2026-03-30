# Verification

## Before Fix

1. Update a record.
2. Immediately read it back through the normal read path.
3. Confirm the old value can appear while the primary already has the new value.

## After Fix

1. Repeat the same write-then-immediate-read flow.
2. Confirm the returned value always reflects the just-written state.
3. Confirm the chosen consistency rule is explicit and intentional.

## Regression Checks

- Test normal read-only flows still use replicas where appropriate.
- Test multiple rapid updates for the same user.
- Test under replica lag or failover scenarios.

