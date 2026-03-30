# Verification

## Before Fix

1. Expire auth token
2. Observe infinite reconnect loop in network tab

## After Fix

1. Expire auth token
2. Confirm auth error handled, no reconnect loop, user redirected to login

## Regression Checks

- Confirm genuine network drops still trigger reconnect
- Test token refresh flow if applicable
