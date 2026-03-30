# Verification

## Before Fix

Login on instance A → next request on instance B → logged out

## After Fix

Login on any instance → session available on all instances

## Regression Checks

Test session persistence after instance restart
