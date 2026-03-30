# Verification

## Before Fix

Deploy without migrate → Invalid column error

## After Fix

Deploy with migrate deploy → schema matches code → no errors

## Regression Checks

Add migration step to all deploy pipelines (CI/CD)
