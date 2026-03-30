# Verification

## Before Fix

Slow delivery + retry → duplicate order created

## After Fix

Retry → event ID already processed → 200 returned without reprocessing

## Regression Checks

Test with forced duplicate event delivery; verify idempotency for all webhook event types
