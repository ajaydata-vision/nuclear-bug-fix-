# Verification

## Before Fix

1. Deploy a changed bundle to origin under the same asset URL.
2. Load the app through the CDN.
3. Confirm the CDN can still serve the old JS.

## After Fix

1. Deploy the same frontend with hashed assets or explicit invalidation.
2. Load through the CDN again.
3. Confirm the new bundle is served immediately.

## Regression Checks

- Test repeat deploys.
- Confirm old bundles can still be cached safely by unique hash.
- Confirm HTML references the new bundle name after each release.

