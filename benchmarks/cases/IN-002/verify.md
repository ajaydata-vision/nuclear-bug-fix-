# Verification

## Before Fix

1. Replay a signed webhook from the provider.
2. Confirm the request reaches the route.
3. Confirm signature verification fails.

## After Fix

1. Replay the exact same signed webhook.
2. Confirm signature verification succeeds.
3. Confirm the event handler receives the parsed body only after verification.

## Regression Checks

- Test multiple event types.
- Test malformed signatures still fail.
- Confirm non-webhook JSON routes still use normal JSON parsing safely.

