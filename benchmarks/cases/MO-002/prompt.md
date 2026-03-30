# MO-002: iOS Layout Breaks Due To Safe Area Inset Not Applied

## User Prompt

Our bottom navigation tab bar is hidden behind the iOS home indicator on newer iPhones. Works fine on Android and older iPhones. What is the bug?

## Context Provided To The Skill

- stack: React Native 0.73, Expo 50, iOS 17
- environment: iOS device with notch/Dynamic Island
- logs:
- bottom navigation bar hidden behind home indicator on iPhone
  - same layout correct on Android and older iPhones
  - no errors
- code excerpt:
```jsx
<View style={{ flex: 1 }}>
  <BottomTabBar />
</View>
```
- reproduction:
1. Run on iPhone 14+ with Dynamic Island
2. Observe bottom nav tab bar hidden behind home indicator
