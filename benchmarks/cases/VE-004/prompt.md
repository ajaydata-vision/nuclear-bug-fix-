# VE-004: Browser API Removed In Chrome Update Breaks Feature Silently

## User Prompt

Our haptic feedback feature silently stopped working in Chrome after a browser update. No errors thrown. Android still works. What happened?

## Context Provided To The Skill

- stack: React 18.2, Chrome 121+
- environment: Chrome browser, production
- logs:
- feature worked until Chrome 121 update
  - navigator.vibrate() returns false but no error
  - Chrome DevTools console shows deprecation warning in Chrome 120
  - Android Chrome still works
- code excerpt:
```js
navigator.vibrate(200)  // haptic feedback
```
- reproduction:
1. Open in Chrome 121 on desktop
2. Trigger action that calls navigator.vibrate()
3. No haptic feedback, function returns false
