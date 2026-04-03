# RN-005: Reanimated Worklet Crash — Accessing Regular JS Variable From UI Thread

## User Prompt

Our swipe-to-dismiss gesture crashes the app in production. In development it works
sometimes. The crash message is `[Reanimated] Tried to synchronously call a non-worklet
function on the UI thread`. I cannot figure out which function is the problem — I am
using Reanimated 3 with `useAnimatedGestureHandler`. What is causing this?

## Context Provided To The Skill

- stack: React Native 0.73.6, react-native-reanimated 3.6.2, react-native-gesture-handler 2.15.0
- versions: iOS 17, Android 14
- environment: production build (crash), development (intermittent)
- logs:
  - `[Reanimated] Tried to synchronously call a non-worklet function on the UI thread`
  - Stack: `at onActive (SwipeDismiss.tsx:18)`
- code excerpt:
```tsx
import Animated, { useSharedValue, useAnimatedGestureHandler, runOnJS } from 'react-native-reanimated';

function SwipeDismiss({ onDismiss, threshold }) {
  const translateX = useSharedValue(0);

  const gestureHandler = useAnimatedGestureHandler({
    onStart: (_, ctx) => {
      ctx.startX = translateX.value;
    },
    onActive: (event, ctx) => {
      translateX.value = ctx.startX + event.translationX;
      if (translateX.value > threshold) {  // threshold is a regular JS prop
        onDismiss();                        // onDismiss is a regular JS function
      }
    },
    onEnd: () => {
      translateX.value = withSpring(0);
    },
  });
  ...
}
```
- reproduction:
  1. Swipe the component past the threshold
  2. `onDismiss` is called inside `onActive`
  3. Crash in production build; intermittent in debug (JS thread is slower, timing changes)
