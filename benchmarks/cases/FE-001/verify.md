# Verification

## Before Fix

1. Build and run the app in production mode.
2. Open `/dashboard`.
3. Refresh the page.
4. Confirm the browser console shows a hydration mismatch warning.

## After Fix

1. Re-run the same page load and refresh flow.
2. Confirm no hydration mismatch warning appears.
3. Confirm the badge still renders a timestamp or placeholder intentionally.

## Regression Checks

- Test both `next dev` and production build.
- Confirm no other server-rendered text uses `Date.now()`, `Math.random()`, or browser-only APIs in render.

