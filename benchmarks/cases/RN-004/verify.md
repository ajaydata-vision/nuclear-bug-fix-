# Verification

## Before Fix
- Camera permission request returns `denied` immediately
- No permission dialog shown on iOS
- Camera screen never activates

## After Fix
1. Add to `ios/MyApp/Info.plist`:
   ```xml
   <key>NSCameraUsageDescription</key>
   <string>We need camera access to scan barcodes.</string>
   ```
   For Expo bare workflow with app.json config: add under `expo.ios.infoPlist` in `app.json`,
   then run `npx expo prebuild --platform ios` before pod install.
2. Run `cd ios && pod install`
3. Rebuild: `npx react-native run-ios`
4. On first launch: iOS permission dialog appears with the usage description string
5. User grants → `status = 'authorized'`, camera activates

## Regression Checks
- User denies permission: status = `denied`, app shows appropriate fallback UI
- Settings > Privacy > Camera: app now appears in the list
- Android: unaffected (Android uses AndroidManifest.xml separately)
