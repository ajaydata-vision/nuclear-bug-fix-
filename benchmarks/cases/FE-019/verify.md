# Verification

## Before Fix

1. Load the site once to install the service worker.
2. Deploy a new asset bundle.
3. Revisit the site normally.
4. Confirm the old hashed bundle or old behavior is still served.

## After Fix

1. Repeat the same deploy-and-revisit flow.
2. Confirm the worker activates the new cache or invalidates the old one.
3. Confirm the updated JS executes without requiring a manual hard refresh.

## Regression Checks

- Test first load, repeat visit, and offline-to-online transitions.
- Confirm no broken offline fallback is introduced.
- Confirm old cache versions are cleaned up safely.

