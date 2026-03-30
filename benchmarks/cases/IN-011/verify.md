# Verification

## Before Fix

Event published with correct source → rule does not match → consumer never called

## After Fix

Fix rule source → events match → consumer triggered

## Regression Checks

Define event source strings as shared constants between publisher and consumer
