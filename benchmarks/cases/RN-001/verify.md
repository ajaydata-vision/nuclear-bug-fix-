# Verification

## Before Fix
- `npx expo start` throws `Unable to resolve module './UserProfile'`
- File `src/components/UserProfile.js` exists and is correct
- Error persists after `rm -rf node_modules && npm install`

## After Fix
1. Stop Metro
2. Run `npx expo start --clear` (Expo) or `npx react-native start --reset-cache` (bare RN)
3. App loads without error
4. `UserProfile` component renders correctly

## Regression Checks
- All other renamed files: confirm no other stale cache entries for old names
- Subsequent restarts without --clear: confirm error does not reappear (cache rebuilt correctly)
