# MO-005: Offline Queue Never Syncs After Reconnect

## User Prompt

Our React Native app lets users edit notes offline. The local changes look fine,
but when the device comes back online the queued edits never sync unless the user
kills and reopens the app. What is the real bug?

## Context Provided To The Skill

- stack: React Native 0.73 + AsyncStorage + NetInfo
- versions: iOS and Android affected
- environment: offline-first mobile app
- logs:
  - offline mutations are persisted locally
  - no sync API call fires on reconnect
  - app relaunch flushes the queue successfully
- code excerpt:

```tsx
useEffect(() => {
  savePendingChange(change);
}, [change]);

async function syncPending() {
  const pending = await loadPendingChanges();
  for (const item of pending) {
    await api.sync(item);
  }
}
```

- reproduction:
  1. Enable airplane mode
  2. Edit a note
  3. Disable airplane mode
  4. Observe no sync until app restart
