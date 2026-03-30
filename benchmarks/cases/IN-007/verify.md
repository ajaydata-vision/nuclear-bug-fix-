# Verification

## Before Fix

Consumer restart → duplicate order created

## After Fix

Consumer restart → idempotency check → existing order found → no duplicate

## Regression Checks

Test consumer restart with pending uncommitted offsets
