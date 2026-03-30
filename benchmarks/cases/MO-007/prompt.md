# MO-007: App Rejected From App Store Due To Missing Permission Usage Description

## User Prompt

Apple rejected our app submission because of a missing Info.plist key even though camera permissions work in development. What is wrong?

## Context Provided To The Skill

- stack: React Native 0.73, Expo 50, iOS
- environment: App Store submission
- logs:
- App Store Connect rejection email: 'Missing Info.plist key NSCameraUsageDescription'
  - app uses camera for QR scanning
  - permission request works in development
- code excerpt:
```xml
<!-- Info.plist — camera key missing -->
<key>NSLocationWhenInUseUsageDescription</key>
<string>For store locator</string>
```
- reproduction:
1. Submit app to App Store
2. Receive rejection citing missing NSCameraUsageDescription
