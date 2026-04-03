# RN-003: AsyncStorage Returns Null On First Launch — App Crashes

## User Prompt

Our app crashes on first install with `TypeError: Cannot read property 'token' of null`.
It works fine after the user logs in and reopens the app. The crash happens before the
login screen even appears. We are reading the auth token from AsyncStorage on startup.
What is causing this?

## Context Provided To The Skill

- stack: React Native 0.72.10, @react-native-async-storage/async-storage 1.21.0
- versions: iOS 17, Android 14
- environment: fresh install (no prior data), first launch only
- logs:
  - `TypeError: Cannot read property 'token' of null`
  - Stack: `at parseStoredAuth (authService.js:12)`
  - Stack: `at App.useEffect (App.tsx:8)`
- code excerpt:
```typescript
// App.tsx
useEffect(() => {
  const initAuth = async () => {
    const stored = await AsyncStorage.getItem('auth');
    // On first install: stored = null (key never written)
    // JSON.parse(null) coerces null to "null" → returns JS null without throwing
    const parsed = JSON.parse(stored);
    if (parsed.token) {  // ← CRASH HERE: TypeError: Cannot read property 'token' of null
      setUser(parsed);
    }
  };
  initAuth();
}, []);
```
- reproduction:
  1. Fresh install on simulator (no prior app data)
  2. Launch app
  3. Crash before login screen appears
  4. Uninstall, reinstall → crash repeats
  5. Complete login flow → relaunch → works correctly
