# MO-001: React Native NativeModule Is Null

## User Prompt

Our React Native app crashes when opening the scanner screen on iOS. Android is
fine. The error is `NativeModule.RNCamera is null`. This started after adding a
new native dependency. What is actually broken?

## Context Provided To The Skill

- stack: React Native 0.73.5 + iOS 17 simulator
- versions: CocoaPods-based iOS project
- environment: iOS build only
- logs:
  - JavaScript runtime error: `NativeModule.RNCamera is null`
  - Xcode build previously succeeded after JS-only changes
- code excerpt:

```tsx
import { RNCamera } from 'react-native-camera';

export function Scanner() {
  return <RNCamera style={{ flex: 1 }} />;
}
```

- reproduction:
  1. `npx react-native run-ios`
  2. Open scanner screen
  3. Observe runtime crash on iOS only
