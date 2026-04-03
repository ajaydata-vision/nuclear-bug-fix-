# React Native Bug Patterns

Covers: Metro bundler, React Navigation, FlatList/SectionList, Animated/Reanimated,
Expo/EAS, State & AsyncStorage, Platform & Permissions, Native Modules & Architecture,
Development tooling interference.

Each pattern: symptom → why → prove → fix.

---

## CATEGORY 1 — METRO BUNDLER & BUILD

### Pattern: Metro cache corruption — module resolution fails after file move or rename
**Symptom:** After renaming a file or moving it between directories, Metro throws `Unable to resolve module './NewName'` or `Module does not exist in the module map`. Correct import path is in the code. Clean reinstall of `node_modules` doesn't fix it.
**Why:** Metro maintains a persistent file map cache. After a file move, the old path still exists in the cache while the new path is not yet indexed. Metro resolves from cache first, finds the old path (now gone), and fails.
**Prove:** Run `npx react-native start --reset-cache`. If the error disappears on first attempt → Metro cache corruption confirmed. No other change needed.
**Fix:** Always run `npx react-native start --reset-cache` after any file rename, move, or directory restructure. Add to CI as a precaution. For Expo: `npx expo start --clear`.

### Pattern: Duplicate module — two versions of the same library in the bundle
**Symptom:** Subtle state inconsistencies. Two components importing from the same package behave as if they have separate instances. Hook state doesn't share. Context values don't propagate. No error, no warning.
**Why:** If a library exists in both the root `node_modules` and a sub-package's `node_modules`, Metro bundles both copies. Each copy has its own module singleton. React context, hook state, and module-level singletons are per-copy.
**Prove:**
```bash
npx react-native info  # shows Metro resolver config
# Also:
node -e "const r = require.resolve('react'); console.log(r)"
# Run from root AND from the suspect sub-package directory
# Different paths = duplicate module
```
Definitive: `yarn why <package>` or `npm ls <package>` — multiple version lines = duplicated.
**Fix:** Hoist to root: add to `package.json` resolutions (yarn) or `overrides` (npm). For monorepos: configure Metro `resolver.extraNodeModules` to point sub-packages at the root copy.

### Pattern: Hermes engine strips console.log in production — debugging data missing
**Symptom:** `console.log` statements visible in development build. Same logs completely absent in production / release build. No crash, no error. Business logic output appears to disappear.
**Why:** Hermes (default JS engine since RN 0.70) strips `console.*` calls in release builds by default. This is intentional. Any debugging that relies on `console.log` in production (e.g., logging to a remote service) is silently removed at bundle time.
**Prove:** In `metro.config.js`, check if `minifierConfig.drop_console` is set. In release `.jsbundle`, search for your log string — if absent, Hermes removed it.
**Fix:** Use a logging library (`react-native-logs`, `@datadog/mobile-react-native`) that calls native platform logging rather than `console.*`. For temporarily preserving logs in release: set `drop_console: false` in Metro minifier config (remove before final production build).

---

## CATEGORY 2 — REACT NAVIGATION

### Pattern: Screen params undefined — wrong navigation method or params not passed
**Symptom:** `route.params` is `undefined` on the destination screen. No error. Screen renders with missing data. Works sometimes, fails other times.
**Why:** Three root causes: (1) `navigation.navigate('Screen')` called without params argument. (2) Screen is navigated to from a tab navigator — tabs don't re-mount on re-navigation, so `setParams` must be used instead. (3) Params defined on a nested navigator's screen but accessed from the wrong nesting level.
**Prove:**
```javascript
// Add at top of destination screen component:
console.log('[NAV] route.params:', JSON.stringify(route.params));
console.log('[NAV] route.name:', route.name);
// If undefined → params not passed. Check the navigate() call site.
// Also log at the navigate() call site:
console.log('[NAV] navigating with params:', JSON.stringify(params));
```
**Fix:**
```javascript
// Passing params
navigation.navigate('ProfileScreen', { userId: user.id });

// Accessing in nested navigator — access via route from the correct navigator level
// Parent screen: route.params.userId
// Nested screen: navigation.getParent()?.getState() if needed
```

### Pattern: Navigation goBack() navigates to wrong screen — stack not structured as expected
**Symptom:** User taps back. Goes to a screen that was not the previous one. Or goes to an unexpected tab. Or navigator resets entirely.
**Why:** React Navigation's stack reflects the actual navigation history, not the UI hierarchy. If `navigate()` is used instead of `push()` for repeated visits, the stack de-duplicates and `goBack()` skips expected screens. Also: modal navigators and nested stacks have separate history — `goBack()` only pops within the current navigator.
**Prove:**
```javascript
// Log the full navigation state to see the actual stack:
console.log('[NAV] state:', JSON.stringify(navigation.getState(), null, 2));
// Shows exact screens in stack and their order
// Compare against expected stack to find where the structure diverges
```
**Fix:** Use `navigation.push('Screen')` (not `navigate`) when you need multiple instances of the same screen in the stack. Use `navigation.popToTop()` to reset a stack explicitly. For cross-navigator back: `navigation.getParent()?.goBack()`.

### Pattern: Screen re-mounts on every navigation — unnecessary unmount/mount cycle
**Symptom:** Heavy screen (with data fetch, animations, maps) re-fetches and re-renders from scratch every time it gains focus. Even when the data hasn't changed. Performance degrades with navigation.
**Why:** Stack navigator keeps screens mounted by default. Tab navigator also keeps screens mounted after first visit. If the screen IS re-mounting, a key prop is changing, the navigator is being re-created, or the screen is inside a conditional that unmounts it.
**Prove:**
```javascript
useEffect(() => {
  console.log('[SCREEN] mounted');
  return () => console.log('[SCREEN] unmounted');
}, []);
// If unmounted/mounted logs fire on every navigation visit → screen is re-mounting
// If only mounted once → screen is re-using, use useFocusEffect for focus-based refresh
```
**Fix:** For focus-based data refresh without remounting: `useFocusEffect(useCallback(() => { fetchData(); }, []))`. For tabs: `lazy={false}` to pre-mount all tabs. For expensive one-time setup: move to a parent navigator screen or use a navigation state listener.

### Pattern: Deep link opens wrong screen or crashes on cold start
**Symptom:** Deep link URL opens the app. Goes to the wrong screen, or crashes immediately on cold start (app was not running). Works correctly when tapped from inside a running app.
**Why:** On cold start, the navigator hasn't finished mounting when the deep link arrives. The linking config path-to-screen mapping is wrong or missing for the target screen. Also: nested navigators require the full path hierarchy in the linking config.
**Prove:**
```javascript
// In linking config, add logging:
const linking = {
  prefixes: ['myapp://'],
  config: { screens: { Home: 'home', Profile: 'profile/:userId' } },
  // Add:
  getStateFromPath: (path, options) => {
    console.log('[DEEPLINK] path received:', path);
    const state = getStateFromPath(path, options);
    console.log('[DEEPLINK] state resolved:', JSON.stringify(state));
    return state;
  }
};
```
**Fix:** Map every deep linkable screen in the `linking.config.screens` object including nested navigator screens using nested object notation. For cold start: ensure navigator is mounted before deep link is processed using a loading state.

---

## CATEGORY 3 — FLATLIST & LIST PERFORMANCE

### Pattern: FlatList re-renders every item on any state change — keyExtractor missing or wrong
**Symptom:** List scrolling is janky. CPU spikes on any parent state update even if list data hasn't changed. Adding one item re-renders the entire list.
**Why:** Without a stable `keyExtractor`, React Native uses array index as the key. On any parent re-render, React diffing by index cannot determine which items changed, re-renders all. Even with `keyExtractor`, if it returns a non-unique or unstable value (timestamp, Math.random()), diffing fails.
**Prove:**
```javascript
// Add to renderItem:
const renderItem = ({ item }) => {
  console.log('[FLATLIST] rendering item id=', item.id);
  return <MyItem item={item} />;
};
// Count log lines on a parent state update that shouldn't affect the list.
// N logs for N items = all items re-rendering = keyExtractor problem.
```
**Fix:**
```javascript
<FlatList
  keyExtractor={(item) => item.id.toString()}  // stable, unique ID
  renderItem={renderItem}
  // Also memoize renderItem:
/>
const renderItem = useCallback(({ item }) => <MyItem item={item} />, []);
// And memoize MyItem:
const MyItem = React.memo(({ item }) => { ... });
```

### Pattern: FlatList scroll position jumps — getItemLayout not provided for variable height items
**Symptom:** Programmatic scroll (`scrollToIndex`, `scrollToOffset`) jumps to wrong position. Or: scrolling near the end of the list causes visible position jump. Works with small lists, breaks with large ones.
**Why:** Without `getItemLayout`, FlatList must measure each item height on mount. Until measured, it estimates — often wrong. `scrollToIndex` uses estimated offsets which don't match actual rendered positions. The longer the list, the larger the accumulated error.
**Prove:** Call `flatListRef.current.scrollToIndex({ index: 50, animated: false })` in a `useEffect`. If the list scrolls to a visually wrong item → offset estimation is wrong → `getItemLayout` needed.
**Fix:**
```javascript
// If items have fixed height:
getItemLayout={(data, index) => ({
  length: ITEM_HEIGHT,
  offset: ITEM_HEIGHT * index,
  index,
})}

// If items have variable but known height (e.g., stored in data):
getItemLayout={(data, index) => ({
  length: data[index].height,
  offset: data.slice(0, index).reduce((sum, d) => sum + d.height, 0),
  index,
})}
```

### Pattern: FlatList blank areas on scroll — removeClippedSubviews unmounts absolutely positioned children
**Symptom:** Scrolling fast reveals blank/white areas where list items should be. Scrolling back shows them again. Only happens on Android or on long lists.
**Why:** `removeClippedSubviews` (default `true` on Android) unmounts items outside the viewport to save memory. If items contain absolutely positioned children that extend outside the item's own bounds, those children are clipped and removed correctly — but blank space appears where they should render.
**Prove:** Set `removeClippedSubviews={false}` temporarily. If blank areas disappear → confirmed. Check if list items use `position: 'absolute'` for any children.
**Fix:** For items with absolute positioning: set `removeClippedSubviews={false}`. For large lists where memory matters: redesign item layout to avoid absolute children extending outside item bounds. Alternatively, increase `windowSize` prop to keep more items rendered.

---

## CATEGORY 4 — ANIMATED & REANIMATED

### Pattern: useNativeDriver: true crashes with layout props — unsupported property animated
**Symptom:** Crash with `Style property 'height' is not supported by native animated module`. Or `width`, `margin`, `padding` etc. Only crashes at runtime, not at build time. Works without `useNativeDriver`.
**Why:** Native driver offloads animation calculations to the UI thread for performance, but only supports a subset of style properties: `transform`, `opacity`. Layout properties (`width`, `height`, `margin`, `padding`, `left`, `top`) cannot be driven natively — they require the JS thread for layout recalculation.
**Prove:** The error message names the exact unsupported property. No additional logging needed. Check every `Animated.Value` used with `useNativeDriver: true` — enumerate which style keys it drives.
**Fix:** Separate animations: use `useNativeDriver: true` only for `transform` and `opacity`. Use `useNativeDriver: false` for layout properties. For performant layout animations: use Reanimated 2+ `useAnimatedStyle` with layout values, or `LayoutAnimation` for simpler cases.

### Pattern: Reanimated 2 worklet crash — accessing JS-side variable from UI thread
**Symptom:** App crashes with `[Reanimated] Tried to synchronously call a non-worklet function on the UI thread`. Or: silent crash/freeze when running animation. Works in development, crashes in production.
**Why:** Reanimated 2 worklets run on the UI thread. They cannot access regular JS variables, hooks, or functions. Only worklet functions (decorated with `'worklet'` directive) and `SharedValue`s can be accessed from the UI thread.
**Prove:**
```javascript
// Add 'worklet' directive check — if a function is called from useAnimatedStyle
// or useAnimatedGestureHandler, it must have 'worklet' at the top:
const myStyle = useAnimatedStyle(() => {
  'worklet'; // this is required
  return { opacity: someSharedValue.value }; // SharedValue access is safe
  // return { opacity: regularJsVar }; // THIS crashes — regular var, not shared
});
```
**Fix:** Convert all functions called from worklets to worklets by adding `'worklet'` directive. Replace JS variable references with `SharedValue`s (created via `useSharedValue`). Use `runOnJS(myJsFunction)(args)` explicitly when you must call JS from UI thread.

### Pattern: Animated loop memory leak — cleanup missing in useEffect
**Symptom:** App runs fine initially. Over time (after several screen navigations or re-mounts), memory usage grows. Animation-heavy screens show increasing memory after repeated visits.
**Why:** `Animated.loop()` with `start()` runs indefinitely. If the component unmounts without calling `animation.stop()`, the animation loop keeps running, holding references to the component's closures and preventing garbage collection.
**Prove:**
```javascript
// Add mount/unmount logging:
useEffect(() => {
  console.log('[ANIM] component mounted');
  const anim = Animated.loop(Animated.sequence([...]));
  anim.start();
  return () => {
    console.log('[ANIM] stopping animation on unmount');
    anim.stop(); // if this line never ran → leak
  };
}, []);
// Navigate away and back repeatedly. Watch memory in Xcode/Android Profiler.
```
**Fix:** Always return a cleanup function from `useEffect` that calls `animation.stop()` or `animation.reset()`. For Reanimated: `cancelAnimation(sharedValue)` in cleanup.

---

## CATEGORY 5 — EXPO & EAS BUILD

### Pattern: Native module available in Expo Go, undefined in standalone build — plugin not configured
**Symptom:** Feature works perfectly in Expo Go development client. After EAS build, the native module is `undefined` or throws `null is not an object`. No build error.
**Why:** Expo Go ships with many native modules pre-bundled. A standalone build only includes what's in your `app.json`/`app.config.js` plugins config. If a native library requires an Expo config plugin (to modify native code) and that plugin is not listed, the native side is missing from the build.
**Prove:**
```javascript
// Add to the module usage point:
import { NativeModules } from 'react-native';
console.log('[NATIVE] available modules:', Object.keys(NativeModules));
// If your module name is absent → native side not built
// Compare Expo Go run vs EAS build run
```
**Fix:** Add the library's config plugin to `app.json`:
```json
{
  "expo": {
    "plugins": [
      ["expo-camera", { "cameraPermission": "..." }],
      "expo-location"
    ]
  }
}
```
Run `npx expo prebuild` to verify native code changes. Then `eas build`.

### Pattern: EAS build succeeds but app crashes on launch — environment variable undefined
**Symptom:** Local development works. EAS build succeeds with no error. App installs. Crashes immediately on launch or shows blank screen.
**Why:** Environment variables available locally (`.env`, shell exports) are not automatically available in EAS builds. EAS build uses its own environment — only variables defined in `eas.json` under `env` or in EAS Secrets are injected.
**Prove:**
```javascript
// Add as early as possible (App.js or index.js):
console.log('[ENV] API_URL:', process.env.EXPO_PUBLIC_API_URL);
console.log('[ENV] all env keys:', Object.keys(process.env).filter(k => k.startsWith('EXPO')));
// In EAS build log: if key is undefined → not injected
```
**Fix:**
```json
// eas.json
{
  "build": {
    "production": {
      "env": {
        "EXPO_PUBLIC_API_URL": "https://api.example.com"
      }
    }
  }
}
```
For secrets: use `eas secret:create`. Prefix client-side variables with `EXPO_PUBLIC_` — only those are embedded in the JS bundle.

### Pattern: OTA update (expo-updates) shows old code — update not applied on launch
**Symptom:** `eas update` completes successfully. User opens app. Old code still running. Sometimes takes multiple app restarts to see new code.
**Why:** `expo-updates` checks for updates in the background after launch by default (`checkAutomatically: "ON_LOAD"`). The current launch uses the previously cached bundle. The new bundle is downloaded but only applied on the NEXT launch. Users on the old code until they close and reopen.
**Prove:**
```javascript
import * as Updates from 'expo-updates';
useEffect(() => {
  console.log('[UPDATES] current update id:', Updates.updateId);
  console.log('[UPDATES] channel:', Updates.channel);
  console.log('[UPDATES] isEmbeddedLaunch:', Updates.isEmbeddedLaunch);
  // If updateId doesn't match latest published → old bundle running
}, []);
```
**Fix:** For critical updates, use `Updates.checkForUpdateAsync()` + `Updates.fetchUpdateAsync()` + `Updates.reloadAsync()` on launch to force immediate reload. For routine updates, the default background check is sufficient. Set `checkAutomatically: "ON_ERROR_RECOVERY"` for production stability.

---

## CATEGORY 6 — STATE & ASYNC STORAGE

### Pattern: AsyncStorage returns null on first install — key doesn't exist yet
**Symptom:** On first app install, `AsyncStorage.getItem('user_token')` returns `null`. Code treats `null` as an error or crashes with `cannot read property of null`. Works fine after first login/setup.
**Why:** `AsyncStorage.getItem()` returns `null` (not an error, not `undefined`) when the key has never been set. This is correct behavior — the key literally doesn't exist yet. Code that doesn't handle `null` as a valid "not yet set" state crashes on first run.
**Prove:**
```javascript
// Add explicit null check logging:
const token = await AsyncStorage.getItem('user_token');
console.log('[STORAGE] token value:', token, 'type:', typeof token);
// null on first launch = expected. crash = unhandled null.
```
**Fix:**
```javascript
const token = await AsyncStorage.getItem('user_token');
if (token === null) {
  // First run or logged out — navigate to login
  navigateToLogin();
  return;
}
// token exists — proceed
```
Never use `if (!token)` — empty string `""` is falsy but a valid (though invalid) token.

### Pattern: Redux action dispatches but UI doesn't update — selector memoization returns stale reference
**Symptom:** `dispatch(updateUser(newUser))` executes. Redux DevTools shows state updated correctly. Component never re-renders. Old data shown.
**Why:** `useSelector` with a selector that returns a derived object (e.g., `state => state.users.list.filter(...)`) creates a new array reference on every call. When the state changes, the selector runs, creates a new array, and React compares by reference — but if the filter result is empty or unchanged in content, `shallowEqual` comparison fails and re-render is skipped. With `createSelector` (Reselect): if input selectors return same references, memoized output returns the same stale reference.
**Prove:**
```javascript
// Add inside component:
const data = useSelector(state => state.users.list);
console.log('[REDUX] selector result ref:', data, 'length:', data?.length);
// Subscribe to store directly to bypass selector:
useEffect(() => {
  const unsubscribe = store.subscribe(() => {
    console.log('[REDUX] store updated:', store.getState().users);
  });
  return unsubscribe;
}, []);
// If store shows new data but component doesn't → selector or equality problem
```
**Fix:** Use `shallowEqual` as second argument to `useSelector` for object/array returns: `useSelector(selector, shallowEqual)`. For complex derived data: use `createSelector` from Reselect with proper input selectors that return primitive-comparable values.

### Pattern: useEffect with async data fetch — stale state update after unmount
**Symptom:** Navigating away quickly while data is loading. App crashes with `Warning: Can't perform a React state update on an unmounted component`. Or: data from the old screen appears briefly on the new screen. Console shows the warning but sometimes no visible bug.
**Why:** `fetch` inside `useEffect` resolves after the component unmounts. The `.then(data => setState(data))` runs on unmounted component. React 18 suppresses the warning but the underlying issue (stale closure + potential race) remains.
**Prove:** Add `console.log('[FETCH] component unmounted before response arrived')` in the cleanup function. If this fires while a fetch is in progress, the stale update is coming.
**Fix:**
```javascript
useEffect(() => {
  let cancelled = false;
  const fetchData = async () => {
    const data = await api.getUser(userId);
    if (!cancelled) setState(data); // guard against unmounted update
  };
  fetchData();
  return () => { cancelled = true; }; // cleanup cancels the update
}, [userId]);
// Or use AbortController for actual request cancellation
```

---

## CATEGORY 7 — PLATFORM & PERMISSIONS

### Pattern: iOS permission request shows no dialog — Info.plist entry missing
**Symptom:** `PermissionsAndroid` (Android) works. On iOS, calling `Camera.requestCameraPermissionsAsync()` or similar does nothing — no dialog, no error. Feature silently unavailable.
**Why:** iOS requires every permission the app might request to have a usage description string in `Info.plist`. Without it, iOS silently denies the request — no dialog, no error thrown to JS. App Store review also rejects apps requesting undeclared permissions.
**Prove:**
```javascript
import { Camera } from 'expo-camera';
const { status } = await Camera.requestCameraPermissionsAsync();
console.log('[PERM] camera status:', status);
// 'denied' on first request with no dialog = Info.plist entry missing
// 'granted' = already approved in a prior session
// Check native iOS logs in Xcode: "This app has crashed because it attempted to 
// access privacy-sensitive data without a usage description."
```
**Fix:** Add to `app.json` under `expo.ios.infoPlist` (Expo) or directly to `ios/MyApp/Info.plist` (bare):
```json
{
  "NSCameraUsageDescription": "We need camera access to scan QR codes.",
  "NSMicrophoneUsageDescription": "We need microphone access to record audio.",
  "NSLocationWhenInUseUsageDescription": "We need location to show nearby results."
}
```
Run `npx expo prebuild` or `pod install` after changing `app.json`.

### Pattern: Android runtime permission granted but feature still fails — permission not in AndroidManifest
**Symptom:** `PermissionsAndroid.request()` returns `'granted'`. Feature still doesn't work. Camera shows black screen, location returns null, microphone silent.
**Why:** Android requires TWO steps: (1) declare permission in `AndroidManifest.xml` — without this, the runtime dialog never appears and `granted` reflects a stale cached value. (2) Request at runtime (`PermissionsAndroid.request()`). Missing the manifest declaration causes the permission to be silently available in debug (dev tools grant it) but fail in release.
**Prove:**
```bash
# Check what permissions are actually in the APK:
aapt dump permissions path/to/app.apk
# If your required permission is absent → AndroidManifest missing it
```
**Fix:** Add to `android/app/src/main/AndroidManifest.xml`:
```xml
<uses-permission android:name="android.permission.CAMERA" />
<uses-permission android:name="android.permission.RECORD_AUDIO" />
```
For Expo: add under `expo.android.permissions` in `app.json`. Rebuild after manifest changes.

### Pattern: iOS safe area content hidden under notch or home indicator
**Symptom:** On iPhone 14+ (Dynamic Island) or iPhone X+ (notch), content at top of screen is hidden behind the notch. Bottom content is hidden behind home indicator bar. Only on real device, not simulator with older iPhone model selected.
**Why:** Without `SafeAreaView` or `useSafeAreaInsets`, content is rendered over the full screen including the hardware safe area. Simulator with older device model doesn't have a notch — bug is invisible in development.
**Prove:** Run on a physical iPhone 14 or select iPhone 14 Pro in Simulator. If content is clipped at top/bottom → safe area not handled.
**Fix:**
```javascript
import { SafeAreaView } from 'react-native-safe-area-context';
// Wrap root screen:
export default function App() {
  return (
    <SafeAreaProvider>
      <SafeAreaView style={{ flex: 1 }}>
        <YourContent />
      </SafeAreaView>
    </SafeAreaProvider>
  );
}
// Or for fine-grained control:
import { useSafeAreaInsets } from 'react-native-safe-area-context';
const insets = useSafeAreaInsets();
<View style={{ paddingTop: insets.top, paddingBottom: insets.bottom }}>
```

---

## CATEGORY 8 — NATIVE MODULES & ARCHITECTURE

### Pattern: Native module null in release build — linked but not initialized
**Symptom:** `NativeModules.MyModule` is defined in debug build. Returns `undefined` or `null` in release build. No linker error. No build failure.
**Why:** Debug builds use the Metro dev server which includes all registered modules. Release builds require the module to be explicitly registered in the native startup code. For iOS: module not added to `AppDelegate`. For Android: module not added to `MainApplication`'s `getPackages()`. ProGuard (Android release) may also strip the class if not in keep rules.
**Prove:**
```javascript
import { NativeModules } from 'react-native';
console.log('[NATIVE] MyModule:', NativeModules.MyModule);
console.log('[NATIVE] all modules:', Object.keys(NativeModules).join(', '));
// Run in RELEASE mode (not debug)
// If MyModule absent → not registered in native startup
```
**Fix:**
- iOS: Add to `AppDelegate.m` / `AppDelegate.swift`. For auto-linking: `pod install` + clean build.
- Android: Add `new MyPackage()` to `getPackages()` in `MainApplication.java`. Add ProGuard keep rule: `-keep class com.myapp.MyModule { *; }`

### Pattern: New Architecture (JSI) module unavailable — TurboModule not enabled or unsupported
**Symptom:** After enabling New Architecture (`newArchEnabled=true` in `gradle.properties`), a native module stops working. Throws `TurboModuleRegistry.getEnforcing(...) Module not found`. Works with Old Architecture.
**Why:** New Architecture uses JSI/TurboModules instead of the Bridge. Libraries must explicitly support TurboModules. Many older libraries have not migrated. Enabling New Architecture without checking library compatibility breaks them.
**Prove:**
```bash
# Check which libraries support New Architecture:
npx react-native info
# Or check each library's README/CHANGELOG for "New Architecture" / "TurboModule" support
# List incompatible libraries:
cd android && ./gradlew :app:dependencies | grep -i "turbo\|jsi"
```
**Fix:** For libraries not yet supporting New Architecture: disable New Architecture (`newArchEnabled=false`) until they do, or find a replacement. For your own native modules: implement `TurboModuleSpec` interface and register with `TurboModuleRegistry`. Check the React Native New Architecture migration guide for each module type.

---

## CATEGORY 9 — DEVELOPMENT TOOLING INTERFERENCE

### Pattern: React Native Debugger / Flipper connected — app behavior differs from production
**Symptom:** Bug is reproducible with debugger/Flipper attached. Cannot reproduce without it. Or: bug only appears in production, never with debugger open.
**Why:** Connecting the JS debugger changes the JS execution environment. Chrome Debugger runs JS in Chrome's V8, not Hermes. Timing changes: async operations execute on Chrome's event loop. Network requests may be proxied differently. Some native calls behave differently when bridge is in debug mode.
**Prove:** Reproduce the bug. Disconnect the debugger completely (close Flipper, close Chrome Debugger tab, disable remote debugging). Does bug persist? If bug disappears → debugger interference. If bug appears only without debugger → Heisenbug with timing dependency on debugger's overhead.
**Fix:** For production-only bugs: build a release build and use Sentry/Bugsnag for crash reporting rather than debugger. For timing bugs exposed by debugger: the debugger revealed a real race condition — fix the race, don't remove the debugger.

### Pattern: Fast Refresh stale state — hook state or module-level variable not reset
**Symptom:** During development, after saving a file, the app hot reloads but shows incorrect state. Old values persist in hooks. A full reload (shake menu → Reload) fixes it.
**Why:** Fast Refresh preserves component state across reloads for components that haven't changed. If a hook's initial state depends on a module-level variable that was mutated, or if a reducer has a bug that only manifests after specific state transitions, Fast Refresh shows the mutated/incorrect state.
**Prove:** Press `R` in Metro terminal (full reload). If the bug disappears → Fast Refresh was showing stale state, not a production bug. If it persists after full reload → real bug.
**Fix:** For development: use full reload when debugging state-related issues. For the underlying bug: never mutate module-level variables that affect initial state. Use `useRef` or `useState` initializer functions for derived initial state.
