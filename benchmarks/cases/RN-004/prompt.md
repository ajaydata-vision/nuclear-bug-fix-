# RN-004: iOS Camera Permission Request Shows No Dialog — Camera Unavailable

## User Prompt

Our barcode scanner screen requests camera permission on mount. On Android the
permission dialog appears correctly. On iOS nothing happens — no dialog, no error,
the permission status comes back as `denied` immediately. The camera never activates.
We have the `react-native-camera` package installed and working on Android. What
is wrong with the iOS setup?

## Context Provided To The Skill

- stack: React Native 0.73.4, react-native-camera 4.2.1, Expo bare workflow
- versions: iOS 17.3, Xcode 15.2
- environment: iOS physical device and simulator
- logs:
  - No Xcode console errors on launch
  - JavaScript: `permissionStatus = 'denied'` logged immediately after request
  - No permission dialog ever shown to user
- code excerpt:
```tsx
import { RNCamera, CameraPermissionStatus } from 'react-native-camera';

useEffect(() => {
  const requestPerm = async () => {
    const status: CameraPermissionStatus = await RNCamera.requestCameraPermissionsAsync();
    console.log('permissionStatus =', status);
    if (status === 'authorized') {
      setHasPermission(true);
    }
  };
  requestPerm();
}, []);
```
- `ios/MyApp/Info.plist` (relevant excerpt):
```xml
<key>NSLocationWhenInUseUsageDescription</key>
<string>We use your location to show nearby stores.</string>
```
