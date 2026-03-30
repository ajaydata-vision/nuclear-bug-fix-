# MO-008: Background Fetch Does Not Trigger On iOS When App Is Terminated

## User Prompt

Our background sync works when the app is in the background but never runs when the user has force-quit the app. Background App Refresh is enabled. What is the bug?

## Context Provided To The Skill

- stack: React Native 0.73, Expo 50, iOS 17
- environment: iOS production, app terminated by user
- logs:
- background sync works when app is in background (not terminated)
  - no background fetch executions when app is force-quit
  - Background App Refresh is enabled in device settings
- code excerpt:
```js
BackgroundFetch.configure({ minimumFetchInterval: 15 }, callback)
```
- reproduction:
1. Enable background fetch in app
2. Force-quit the app from iOS app switcher
3. Wait 15 minutes
4. Observe no background fetch occurred
