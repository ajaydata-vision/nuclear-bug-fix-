# Verification

## Before Fix

1. Navigate routes 10x
2. Confirm listener count in DevTools growing

## After Fix

1. Add cleanup
2. Navigate same routes
3. Confirm listener count stable

## Regression Checks

- Audit other global event listeners in the codebase
- Test all useEffect hooks that add external subscriptions
