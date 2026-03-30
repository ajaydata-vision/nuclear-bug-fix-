# Verification

## Before Fix

1. Connect on fast network with server sending immediate message
2. Log all received messages
3. Confirm first message sometimes missing

## After Fix

1. Repeat with handler attached synchronously
2. Confirm all messages including first are received

## Regression Checks

- Test onerror and onclose handlers also attached before async boundary
- Test reconnection logic
