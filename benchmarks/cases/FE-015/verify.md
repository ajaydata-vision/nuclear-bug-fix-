# Verification

## Before Fix

1. Make cross-origin credentialed request
2. Confirm CORS error

## After Fix

1. Repeat request after CORS config update
2. Confirm cookies sent and response received

## Regression Checks

- Confirm CORS does not allow arbitrary origins in production
- Test preflight for all HTTP methods
