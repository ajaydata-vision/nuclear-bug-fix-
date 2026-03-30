# MO-006: Deep Link Navigation Fails When App Is Cold-Started

## User Prompt

Deep links work when our app is already open but navigate to the home screen instead of the correct screen when the app is cold-started. What is the bug?

## Context Provided To The Skill

- stack: React Native 0.73, React Navigation 6, Expo 50
- environment: iOS and Android
- logs:
- deep link myapp://product/123 opens app to home screen instead of product page
  - deep link works correctly if app is already running
  - getLinking() URL is received but navigation happens before navigator is ready
- code excerpt:
```js
Linking.getInitialURL().then(url => {
  if (url) navigate(parseUrl(url))
})
```
- reproduction:
1. Close app completely
2. Click deep link myapp://product/123
3. App opens to home screen not product page
