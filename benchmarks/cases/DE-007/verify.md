# Verification

## Before Fix

Merge to main → staging updated, production not updated

## After Fix

Add --env production → main merge updates production

## Regression Checks

Add deployment target verification step to CI (check which environment was actually updated)
