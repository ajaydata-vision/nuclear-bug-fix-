# Verification

## Before Fix
- Fresh install → crash before login screen
- `TypeError: Cannot read property 'token' of null`

## After Fix
```typescript
const stored = await AsyncStorage.getItem('auth');
if (!stored) {
  // First launch — no stored auth, navigate to login
  setAuthState('unauthenticated');
  return;
}
const parsed = JSON.parse(stored);
if (parsed?.token) {
  setUser(parsed);
  setAuthState('authenticated');
} else {
  setAuthState('unauthenticated');
}
```
1. Fresh install → no crash, login screen appears
2. After login → auth stored, relaunch loads user correctly

## Regression Checks
- Logout (clears storage) then relaunch: same as first install — no crash, login screen
- Corrupted storage value: JSON.parse throws — add try/catch around parse for robustness
- Null token inside valid JSON: `parsed?.token` guard handles this correctly
