# Verification

## Before Fix

Network drop → reconnect → N WebSocket instances → N duplicate notifications

## After Fix

Reconnect closes old WS first → single active instance → no duplicates

## Regression Checks

Test multiple rapid reconnects; verify DevTools shows only one active WebSocket connection
