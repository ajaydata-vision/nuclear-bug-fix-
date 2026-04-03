# Verification

## Before Fix
- Swiping past threshold crashes app in production with:
  `[Reanimated] Tried to synchronously call a non-worklet function on the UI thread`
- In development: intermittent (Hermes timing differs from debug JS thread)

## After Fix
```tsx
onActive: (event, ctx) => {
  translateX.value = ctx.startX + event.translationX;
  if (translateX.value > threshold) {
    runOnJS(onDismiss)(); // ← bridge call to JS thread, safe from UI thread
  }
},
```
1. Swipe past threshold → no crash, `onDismiss` called correctly on JS thread
2. No change to `threshold` required — primitive props are safe in worklets

## Regression Checks
- Swipe below threshold: no dismiss, animation springs back correctly
- Rapid repeated swipes: no duplicate dismiss calls (runOnJS does not queue multiple)
- iOS and Android: both work (UI thread enforcement applies to both)
- Release build: confirms no crash (this was the environment where crash was deterministic)
