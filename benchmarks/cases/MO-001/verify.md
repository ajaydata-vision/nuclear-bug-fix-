# Verification

## Before Fix

1. Run the iOS app build.
2. Open the scanner screen.
3. Confirm `NativeModule... is null` appears and the screen fails.

## After Fix

1. Reinstall pods or relink the dependency and rebuild the iOS app.
2. Open the same scanner screen.
3. Confirm the native module loads and the screen renders.

## Regression Checks

- Confirm Android still works.
- Confirm a clean clone and fresh iOS build also succeed.
- Confirm permission-denied behavior is handled separately from module loading.

