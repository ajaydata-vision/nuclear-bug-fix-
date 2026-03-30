# Verification

## Before Fix

1. Hard refresh any non-root SPA route
2. Confirm 404

## After Fix

1. Update Nginx config and reload
2. Hard refresh same route
3. Confirm SPA loads correctly

## Regression Checks

- Confirm actual missing static files still return 404 (not swallowed by SPA)
- Test API routes are not caught by the fallback
