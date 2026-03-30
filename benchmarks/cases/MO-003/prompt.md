# MO-003: Push Notification Token Not Updated After App Reinstall

## User Prompt

Users who reinstall our app stop receiving push notifications. The server has their old token but notifications never arrive. What is the real bug?

## Context Provided To The Skill

- stack: React Native 0.73, Expo Notifications, Firebase Cloud Messaging
- environment: iOS and Android production
- logs:
- push notifications stopped for users who reinstalled the app
  - server still has old token
  - new token generated on reinstall but not sent to server
  - token stored in server DB is stale
- code excerpt:
```js
// Only requests token on first install
useEffect(() => {
  if (!tokenSentToServer) {
    registerForPushNotifications().then(sendTokenToServer)
  }
}, [])
```
- reproduction:
1. Install app, register token
2. Uninstall and reinstall
3. Observe push notifications not received
