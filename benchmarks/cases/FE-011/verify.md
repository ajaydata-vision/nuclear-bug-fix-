# Verification

## Before Fix

1. Build and confirm API_URL is undefined in bundle

## After Fix

1. Rename to VITE_API_URL
2. Rebuild
3. Confirm variable is available

## Regression Checks

- Scan all env var references for missing prefix
- Ensure no actual secrets are accidentally prefixed
