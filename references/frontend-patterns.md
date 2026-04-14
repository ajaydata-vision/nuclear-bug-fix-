# Frontend Bug Patterns

Stack-agnostic. Applies to React, Vue, Angular, Svelte, vanilla JS, or any frontend framework.
Each pattern: symptom → why → how to prove → how to fix.

---

## CATEGORY 1 — RENDERING & DISPLAY

### Pattern: Component renders but shows wrong data
**Symptom:** UI displays, but values are stale, missing, or from a previous render.
**Why:** State not updated before render. Computed value cached. Props not passed down. Wrong variable referenced.
**Prove:** Add a log/console at render time printing the exact data being used. Does it match what's displayed?
**Fix:** Trace data flow from source to render. Find where it diverges. Ensure reactive binding is correct.

### Pattern: UI flickers or renders twice
**Symptom:** Component briefly shows wrong state, then corrects itself. Or renders, clears, then renders again.
**Why:** State initialized as null/empty then set async. Two conflicting state updates. Strict mode double-invoke (dev only).
**Prove:** Add a counter — how many times does the render function execute? Log state at each render.
**Fix:** Initialize state with correct default. Batch state updates. Use loading state to suppress early render.

### Pattern: Hydration mismatch (SSR frameworks)
**Symptom:** Works on server, breaks on client. Console error: "hydration mismatch" or "content did not match."
**Why:** Server renders different HTML than client. Usually: Date.now(), Math.random(), browser-only APIs, user-specific data, or non-deterministic rendering.
**Prove:** Compare server-rendered HTML with client HTML. They will differ at a specific node.

### Pattern: Infinite render loop
**Symptom:** Browser tab freezes. CPU spikes. "Maximum update depth exceeded" error.
**Why:** State update inside render body (not in event handler). useEffect dependency array missing or wrong. Circular reactive dependency.
**Prove:** Log every render with a counter. Counter grows without bound = loop.
**Fix:** Move state updates out of render. Fix useEffect deps array. Remove circular dependencies.

### Pattern: Component not re-rendering when data changes
**Symptom:** Data updated in store/state. UI stays frozen on old value.
**Why:** Mutation of object/array instead of replacement (framework doesn't detect mutation). Wrong subscription. Memoization too aggressive.
**Prove:** Log the state value directly from the store vs what's displayed. If different → subscription broken.
**Fix:** Replace objects/arrays instead of mutating. Fix subscription. Adjust memoization condition.

---

## CATEGORY 2 — CSS & LAYOUT

### Pattern: CSS works in dev, broken in prod
**Symptom:** Styles correct locally. Broken or missing in production build.
**Why:** CSS purging removing used classes (Tailwind/PurgeCSS). CSS modules hash different. Import order changed by bundler. Missing PostCSS plugin in prod.
**Prove:** Inspect prod page. Check if class names exist in DOM but no matching CSS rule. Check network tab for CSS file.
**Fix:** Whitelist dynamic class names in purge config. Check CSS import order. Verify PostCSS config runs in prod.

### Pattern: Z-index not working as expected
**Symptom:** Element visually behind another despite high z-index. Tooltip/modal hidden.
**Why:** Stacking context not established. Parent has `transform`, `opacity`, `filter`, or `isolation` creating a new stacking context. z-index only works on positioned elements.
**Prove:** In devtools, inspect the stacking context of the parent elements.
**Fix:** Set `position: relative/absolute/fixed` on the element. Or restructure DOM to avoid nested stacking contexts.

### Pattern: Flexbox/Grid layout breaks on specific content
**Symptom:** Layout correct for typical content. Breaks with long text, images, or different data.
**Why:** No overflow handling. `min-width: auto` on flex children. Implicit grid row height wrong. Content expanding past container.
**Prove:** Test with very long text, very short text, missing data, and oversized images.
**Fix:** Add `overflow: hidden/ellipsis`. Set explicit `min-width: 0` on flex children. Use `max-width` constraints.

### Pattern: CSS variable not applying
**Symptom:** CSS custom property set but element ignores it.
**Why:** Variable defined on wrong scope. Typo in variable name. Specificity override. Not supported in pseudo-elements without workaround.
**Prove:** In devtools computed styles, check if variable is listed and has the expected value at that element.
**Fix:** Define variable on correct ancestor (`:root` for global). Fix typo. Check specificity.

### Pattern: Mobile layout broken, desktop fine
**Symptom:** Layout correct on desktop. Broken on mobile or specific viewport sizes.
**Why:** Viewport meta tag missing. Fixed pixel widths. Touch events not handled. Overflow-x from child element. Font size not scaling.
**Prove:** Use devtools responsive mode. Also test on real device — they differ.
**Fix:** Add `<meta name="viewport">`. Use relative units. Handle touch events. Find the element causing overflow-x.

---

## CATEGORY 3 — STATE MANAGEMENT

### Pattern: State persists across pages/sessions (when it shouldn't)
**Symptom:** Previous user's data visible to new user. Old form values appear on fresh load.
**Why:** Global store not reset between sessions. Module-level variable persists across SSR requests. localStorage not cleared.
**Prove:** Open incognito window. Does it show the stale state? If no → session/storage leak.
**Fix:** Reset global state on logout. Clear localStorage on session end. For SSR — create new store instance per request.

### Pattern: State update lost in concurrent updates
**Symptom:** Clicking quickly or multiple rapid events → only last update applied. Intermediate states lost.
**Why:** State update based on stale snapshot. Each update reads old state, overwrites previous update.
**Prove:** Click the button 5 times rapidly. Expected count: 5. Actual count: 1 or 2 = stale closure.
**Fix:** Use functional state update: `setState(prev => prev + 1)` instead of `setState(count + 1)`.

### Pattern: Store action fires, state unchanged
**Symptom:** Redux/Zustand/Pinia action dispatched. No state change. No error.
**Why:** Reducer returns old state unchanged. Wrong action type string. Mutation inside reducer (Redux). Selector not subscribed to correct slice.
**Prove:** Log the action payload AND the state before/after in the reducer. Are they reaching the right reducer?
**Fix:** Ensure reducer returns new object (not mutated). Verify action type string exact match. Check selector path.

---

## CATEGORY 4 — ROUTING & NAVIGATION

### Pattern: Route change but component doesn't update
**Symptom:** URL changes. Page looks the same. Component doesn't re-mount or re-fetch.
**Why:** Component cached/memoized. Router uses same component instance across routes. Params changed but component didn't detect it.
**Prove:** Log route params inside the component on every render. Do they update when URL changes?
**Fix:** Use route params as part of component key to force re-mount. Or add watcher/effect on route params.

### Pattern: 404 on page refresh (SPA)
**Symptom:** Navigation works within the app. Refreshing the page gives 404.
**Why:** Server returns 404 for any path not explicitly configured. SPA routing is client-side only — server must return index.html for all paths.
**Prove:** Refresh the page on a non-root route. Check server response in Network tab.
**Fix:** Configure server to return index.html for all routes. For Nginx: `try_files $uri /index.html`. For Express: catch-all route.

### Pattern: Query params lost after navigation
**Symptom:** URL has query params. After navigating, they disappear.
**Why:** Navigation replacing URL without preserving existing params. Router link not including current params.
**Prove:** Log the full URL before and after navigation.
**Fix:** Merge current query params into navigation target explicitly.

---

## CATEGORY 5 — FORMS & USER INPUT

### Pattern: Form submission fires but nothing happens
**Symptom:** User clicks submit. No error. No navigation. No API call.
**Why:** Form `submit` event being caught and `.preventDefault()` never called — or called in wrong place. Or: validation silently failing. Or: handler not attached.
**Prove:** Add a log as the FIRST line of the submit handler. Not printed = handler not reached.
**Fix:** Verify handler is attached. Call `e.preventDefault()`. Log validation result explicitly.

### Pattern: Input value not binding to state
**Symptom:** User types in input. State doesn't update. Or state updates but input doesn't reflect it.
**Why:** Missing `onChange`/`v-model`/`[(ngModel)]`. Controlled vs uncontrolled mismatch. State update async gap.
**Prove:** Log state value on every keystroke. Does it lag or not update?
**Fix:** Add correct two-way binding for your framework. Ensure controlled component pattern is consistent.

### Pattern: Validation passes but API rejects data
**Symptom:** Frontend validation passes. API returns 400/422. Data seems correct on screen.
**Why:** Frontend validates display value. API receives serialized/transformed value which is different. Trailing spaces, encoding, type mismatch (string vs number).
**Prove:** Log the EXACT payload being sent to the API. Not the form field values — the serialized body.
**Fix:** Validate the serialized payload, not the display value. Trim/sanitize before sending.

---

## CATEGORY 6 — ASYNC DATA & API CALLS

### Pattern: Data loads then disappears
**Symptom:** Data appears briefly on screen. Then replaced by empty/loading state.
**Why:** Two async calls racing. Second call resolves with empty data after first. Component unmounts and cancels request. State reset triggered after fetch.
**Prove:** Log every state update with timestamp. Which update sets it to empty? What triggered that update?
**Fix:** Cancel in-flight requests on new request (AbortController). Check for unintended state resets.

### Pattern: API called on every keystroke (performance / rate limit)
**Symptom:** Network tab shows flood of requests as user types. Rate limit hit.
**Why:** Search/autocomplete API call in onChange handler without debounce.
**Prove:** Type a 5-character word quickly. Count API calls in network tab. Should be 1, not 5.
**Fix:** Debounce the API call (300-500ms). Cancel previous request before new one fires.

### Pattern: Loading spinner never goes away
**Symptom:** Loading state stuck forever. No error visible. Content never appears.
**Why:** Promise rejected but `isLoading` never set to false. Error caught silently. Finally block missing.
**Prove:** Log every state transition: `loading=true`, `loading=false`. Is the false ever logged?
**Fix:** Always set `isLoading = false` in `finally` block, not just in `try` and `catch`.

### Pattern: Optimistic UI desyncs from server under rapid mutations or slow network
**Symptom:** Counter or UI state flashes wrong values briefly before correcting. Only on slow connections or when the same action fires rapidly. The value shown is never consistent with either the old or new server state. Self-corrects after a delay — which is the diagnostic signal that the *server* is authoritative and the *client* optimistic state is the bug.
**Why:** Multiple optimistic mutations are in-flight simultaneously. Each mutation independently snapshots cache state, applies its own delta, and on success overwrites the cache with whatever it computed locally. When responses arrive out of order:
1. Click A snapshots `likes=5`, optimistically writes `6`, sends request.
2. Click B snapshots `likes=6`, optimistically writes `7`, sends request.
3. B's response arrives first → server returns `6` → handler overwrites cache with `6`, erasing A's effect.
4. A's response arrives → server returns `7` → cache flips back to `7`.
The visible flash is real desync, not a render glitch. **Debouncing the button does NOT fix this** — slow networks reproduce the same race with one click and a navigation.
**Prove:** Throttle to 3G in DevTools. Trigger the mutation 3–4 times rapidly. Watch the counter — it will flash values that are neither the old nor the correct new value. Also: log every mutation's `onMutate`, `onSuccess`, `onSettled` with a request ID — the interleaving of IDs across the three callbacks is the smoking gun.
**Fix:** Use all three TanStack Query mutation handlers together. **Each handler covers a distinct race window. Missing any one breaks the contract:**
- `onMutate` → **cancel in-flight refetches** (otherwise a stale GET response arriving mid-mutation overwrites the optimistic value) AND **snapshot the previous cache value** (the only way to roll back on error).
- `onError` → **roll back to the snapshot** (otherwise a failed mutation leaves the optimistic delta in place forever).
- `onSettled` → **invalidate and refetch** the query unconditionally, success or failure (this is what eliminates accumulated desync from out-of-order responses — the server becomes the single source of truth after every mutation, so no amount of interleaving can leave the cache wrong).
```js
// Define queryKey as a constant matching the key used in useQuery
const POST_QUERY_KEY = ['post', postId]

useMutation({
  mutationFn: updateFn,
  onMutate: async () => {
    await queryClient.cancelQueries({ queryKey: POST_QUERY_KEY })    // cancel in-flight refetches
    const previous = queryClient.getQueryData(POST_QUERY_KEY)        // snapshot before change
    queryClient.setQueryData(POST_QUERY_KEY, (old) => ({
      ...old,
      likes: old.likes + 1,                                           // apply optimistic change
    }))
    return { previous }                                               // return for rollback
  },
  onError: (_err, _vars, context) => {
    queryClient.setQueryData(POST_QUERY_KEY, context.previous)       // rollback on failure
  },
  onSettled: () => {
    queryClient.invalidateQueries({ queryKey: POST_QUERY_KEY })      // always refetch truth
  },
})
```
`onSettled` refetches the authoritative server value after every mutation — success or failure — eliminating accumulated desync regardless of response order.

---

## CATEGORY 7 — WEBSOCKET & REAL-TIME

### Pattern: WebSocket connects, messages not received
**Symptom:** Connection established (confirmed in Network tab). Server sends messages. Client doesn't display them.
**Why:** `onmessage` handler not attached. Message arrives before handler set. JSON.parse failing silently. Wrong event name in custom WS library.
**Prove:** Log EVERY message event: `ws.onmessage = e => console.log('RAW MSG', e.data)`.
**Fix:** Attach handler before connecting. Handle parse errors explicitly. Log raw data before processing.

### Pattern: WebSocket reconnects in a loop
**Symptom:** Connection dropped. Client reconnects. Immediately dropped again. Repeat forever.
**Why:** Server closes connection with specific code (auth error, rate limit). Client reconnects without fixing root cause.
**Prove:** Log the close code and reason: `ws.onclose = e => console.log(e.code, e.reason)`.
**Fix:** Handle close codes. Code 1008 = policy violation (auth). Fix the root cause before reconnecting.

---

## CATEGORY 8 — BUILD & BUNDLE

### Pattern: Works in dev, broken in production build
**Symptom:** Dev server fine. Production build broken. May have no error, just wrong behavior.
**Why:** Tree-shaking removing code incorrectly. Minification breaking dynamic property access. Environment variables not injected. Source maps missing — wrong file evaluated.
**Prove:** Build locally with prod config. Run prod build locally. Does it break locally too?
**Fix:** Check env var injection in build config. Avoid dynamic property access that breaks minification. Add `/*@__PURE__*/` hints if needed.

### Pattern: Bundle size suddenly large / build slow
**Symptom:** Bundle size doubled. Build time 3x longer after adding a dependency.
**Why:** Dependency pulling in huge transitive dep. No tree-shaking (CommonJS vs ESM). Entire library imported instead of specific function.
**Prove:** Run bundle analyzer. Identify the largest chunks. Trace to source.
**Fix:** Import only what you need. Use ESM versions of libraries. Replace heavy deps with lighter alternatives.

### Pattern: Environment variable undefined in browser
**Symptom:** `process.env.VARIABLE` is undefined at runtime. Works in Node, not in browser.
**Why:** Build tool not injecting env vars. Wrong prefix (Vite needs `VITE_`, CRA needs `REACT_APP_`). Server-side var exposed to client (or vice versa).
**Prove:** `console.log(import.meta.env)` or `console.log(process.env)` in browser. What's actually there?
**Fix:** Use correct prefix for your build tool. Configure build tool to inject vars. Never expose secrets to browser.

---

## CATEGORY 9 — BROWSER COMPATIBILITY & APIS

### Pattern: Works in Chrome, broken in Safari/Firefox
**Symptom:** Feature works in one browser, fails silently or errors in another.
**Why:** Non-standard API used. CSS property not supported. JS feature requires polyfill. Different default behavior (date parsing, event handling).
**Prove:** Open browser console in the failing browser. Check for errors/warnings.
**Fix:** Check caniuse.com for the API/property. Add polyfill. Use feature detection before using the API.

### Pattern: CORS error on API call
**Symptom:** API call fails with "CORS policy" error. Works in Postman or curl.
**Why:** Server not returning correct `Access-Control-Allow-Origin` header. Preflight OPTIONS request failing. Credentials mode mismatch.
**Prove:** Check Network tab → failed request → Response headers. Is `Access-Control-Allow-Origin` present?
**Fix:** Fix server CORS config. For credentials: server must set specific origin (not `*`) and client must set `credentials: 'include'`.

### Pattern: localStorage/sessionStorage not working
**Symptom:** Data not persisted. Errors in some browsers. Works in most, fails in one.
**Why:** Private/incognito mode blocks storage in some browsers. Storage quota exceeded. Cross-origin iframe restriction. Third-party cookie blocking affecting storage.
**Prove:** Try/catch around all storage calls. Log the actual error.
**Fix:** Always wrap storage in try/catch. Provide fallback (in-memory). Check quota before writing.

---

## CATEGORY 10 — PERFORMANCE & MEMORY (FRONTEND)

### Pattern: Page works, then becomes slow over time
**Symptom:** Fast on load. Slows progressively. Especially after navigating between pages.
**Why:** Event listeners not removed on component unmount. Intervals/timers not cleared. WebSocket connections not closed. Growing in-memory list never truncated.
**Prove:** Open DevTools Memory tab. Take heap snapshot. Navigate around. Take another snapshot. Compare — what's growing?
**Fix:** Remove event listeners in cleanup (useEffect return, beforeDestroy). Clear intervals. Close connections on unmount.

### Pattern: Scroll or animation jank
**Symptom:** Smooth in dev. Jank/stutter in prod or on low-end device. Includes content jumping unexpectedly (visual jank caused by layout shifts).
**Why:** Layout thrashing (read then write DOM in loop). Expensive computation on main thread. Non-GPU-accelerated CSS properties being animated. Or: elements without explicit dimensions causing layout shifts on load (CLS).
**Prove:**
- **Motion jank** (stutter, dropped frames): Open DevTools Performance tab. Record the jank. Look for long tasks (red bars) and purple layout events in the flame chart.
- **Visual jank** (content jumping): Paste in DevTools console to identify exactly which element is shifting and by how much:
```javascript
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (!entry.hadRecentInput) {
      console.log('[CLS] shift score:', entry.value);
      entry.sources?.forEach(s => {
        console.log('  shifted element:', s.node);
        console.log('  from:', s.previousRect);
        console.log('  to:', s.currentRect);
      });
    }
  }
}).observe({ type: 'layout-shift', buffered: true });
```
If output shows a specific element shifting → that element is missing explicit dimensions or is being injected above existing content.
**Fix:** Use `transform` and `opacity` for animations (GPU-accelerated). Move computation to Web Worker. Batch DOM reads/writes with `requestAnimationFrame`. For layout shifts: add explicit `width`/`height` or `aspect-ratio` to images and embeds; never inject content above the viewport fold.

### Pattern: Page interactions sluggish — clicks and taps respond slowly
**Symptom:** Page loads fine. But clicking buttons, typing, or tapping feels delayed — the UI updates 300–800ms after the action. Lighthouse or CrUX shows INP (Interaction to Next Paint) > 200ms.
**Why:** INP = Input Delay + Processing Time + Presentation Delay. If the main thread is busy with a long task when the user clicks, the event handler is queued (input delay). If the handler itself does heavy work, that adds processing time. Either causes the interaction to feel unresponsive.
**Prove:** Paste in DevTools console, then click/tap the elements that feel slow:
```javascript
new PerformanceObserver((list) => {
  for (const entry of list.getEntries()) {
    if (entry.duration > 200) {
      console.warn('[INP] slow interaction:', {
        type: entry.name,
        totalMs: Math.round(entry.duration),
        inputDelayMs: Math.round(entry.processingStart - entry.startTime),
        processingMs: Math.round(entry.processingEnd - entry.processingStart),
        presentationMs: Math.round(entry.duration - (entry.processingEnd - entry.startTime)),
        target: entry.target
      });
    }
  }
}).observe({ type: 'event', buffered: true, durationThreshold: 16 });
```
Read the output: **high inputDelayMs** → main thread blocked before handler runs (long task blocking). **High processingMs** → event handler itself is doing too much. **High presentationMs** → excessive re-render after handler.
**Fix:** For high input delay: break up long tasks with `setTimeout(fn, 0)` or `scheduler.yield()`. For high processing: move heavy work out of the click handler into `requestAnimationFrame` or a Web Worker. For high presentation: reduce component re-render scope (React.memo, useMemo).

### Pattern: Page loads slowly — LCP element identified but cause unknown
**Symptom:** Page feels slow on initial load. Lighthouse shows LCP (Largest Contentful Paint) > 2.5s. The hero image or main heading takes too long to appear. Users see blank space where content should be.
**Why:** LCP is delayed by one of four causes — each requires a different fix: (1) slow server response (TTFB > 800ms), (2) render-blocking CSS/JS in `<head>` delaying paint, (3) LCP resource discovered late (not preloaded), (4) LCP element rendered client-side after JS runs (not in initial HTML).
**Prove:** First identify your LCP element and its time. Paste in DevTools console:
```javascript
new PerformanceObserver((list) => {
  const last = list.getEntries().at(-1);
  console.log('[LCP] element:', last.element);
  console.log('[LCP] time (ms):', Math.round(last.startTime));
  console.log('[LCP] url (if resource):', last.url);
}).observe({ type: 'largest-contentful-paint', buffered: true });
```
Then diagnose the cause using the LCP time and Network tab:
- LCP time ≈ TTFB → slow server. Fix: CDN, caching, edge rendering.
- LCP time ≈ when CSS finishes loading → render-blocking stylesheet. Fix: inline critical CSS, defer rest.
- LCP url shows image loaded late (starts well after page load in waterfall) → missing preload. Fix: `<link rel="preload" href="..." as="image" fetchpriority="high">`.
- LCP element is `null` in script output → element added by JavaScript, not in HTML. Fix: server-side render or static generate the LCP content.
**Fix:** Match the fix to the cause identified above. Never prescribe a generic "optimize images" without first running this Prove — the four causes require completely different interventions.

---

## CATEGORY 11 — MOBILE (React Native / iOS / Android)

> **React Native bugs: load `references/react-native-patterns.md` instead.**
> That file has 26 dedicated patterns across Metro, React Navigation, FlatList,
> Reanimated, Expo/EAS, AsyncStorage, native modules, permissions, and architecture.
> The patterns below are retained only for **non-React-Native** native iOS/Android apps.

### Pattern: React Native bridge error / native module crash
**Symptom:** App crashes or freezes. "NativeModule is null". Bridge exception in logs.
**Why:** Native module not linked. Platform mismatch. Old RN architecture (Bridge) vs New (JSI). Missing permission.
**Prove:** Run `adb logcat` (Android) or Xcode console (iOS). Look for native exception stack.
**Fix:** Re-run `pod install` (iOS). `npx react-native clean`. Check native module linking. For New Architecture: ensure module supports JSI.

### Pattern: Works on Android, broken on iOS (or vice versa)
**Symptom:** Feature working on one platform, silently failing on the other.
**Why:** Platform-specific API behavior. Font rendering. Shadow/elevation differences. Date parsing differences. Permissions model differs.
**Prove:** Run on both simulators side by side. Check `Platform.OS` branches. Log platform at failure point.
**Fix:** Add platform-specific code. Use `Platform.select()`. Test on real device — simulators hide some bugs.

### Pattern: App freezes / ANR on Android
**Symptom:** App becomes unresponsive. Android shows "App Not Responding". iOS watchdog kills it.
**Why:** Heavy computation on main/UI thread. Synchronous network call. Long-running operation blocking JS thread.
**Prove:** Android: check logcat for "ANR in". iOS: capture crash report from device. Look for main thread blocking calls.
**Fix:** Move heavy work to background thread / worker. Use `InteractionManager.runAfterInteractions()`. Never do sync I/O on main thread.

### Pattern: Push notification not received
**Symptom:** Notification sent (confirmed in server logs). Device never shows it.
**Why:** Device token stale/expired. Permission not granted. Background app refresh disabled. Certificate expired (iOS). FCM/APNs config wrong.
**Prove:** Check push delivery logs on server. Verify token is current. Check device settings for notification permission.
**Fix:** Refresh device token on every app launch. Verify FCM/APNs credentials. Test with direct API call to FCM bypassing your server.

### Pattern: Offline data not syncing when reconnected
**Symptom:** User works offline. Comes back online. Changes lost or not pushed.
**Why:** Sync logic not triggered on reconnect. Conflict resolution not implemented. Queue cleared on restart.
**Prove:** Toggle airplane mode. Make changes. Reconnect. Check if sync fires. Log network state changes.
**Fix:** Use `NetInfo.addEventListener` to trigger sync on reconnect. Persist queue to AsyncStorage/SQLite. Handle conflict resolution explicitly.

### Pattern: Memory warning / app killed on device
**Symptom:** App works fine then suddenly closes. More frequent on older devices.
**Why:** Memory leak. Large images not released. Too many components mounted. Redux store growing unbounded.
**Prove:** Xcode Memory Graph (iOS). Android Memory Profiler. Watch memory usage as you navigate.
**Fix:** Unmount unused components. Compress images. Paginate lists (FlatList, not ScrollView with all items). Clear old data from store.

---

## CATEGORY 12 — SERVICE WORKER vs CDN DISAMBIGUATION

### Pattern: Stale assets after deploy — is it CDN or Service Worker?

This disambiguation is critical because the fix is completely different.

**Prove:** Run these two checks in sequence — the combination gives a definitive answer:
```
1. Hard refresh (Ctrl+Shift+R) on the affected page.
   FIXED → Service Worker. Hard refresh bypasses SW cache; CDN is unaffected by it.
   STILL STALE → Not SW alone. Continue to step 2.

2. Open DevTools → Application → Service Workers.
   SW registered and active? → Open Cache Storage → find your cache → inspect asset URLs.
   Asset present with old content hash → SW is serving stale. Fix: update CACHE_VERSION.
   No SW registered → pure CDN or browser cache issue.

3. Fetch the asset directly from the origin URL (bypass CDN):
   curl -I https://origin.yourdomain.com/app.abc123.js
   Fresh response → CDN is caching stale. Fix: purge CDN or use content-hashed filenames.
   Stale response → Origin itself serving old file. Fix: deployment did not complete.
```
**Geographic test (CDN edge):** If only some users see stale — CDN edge node cache. Other users hit different edge nodes already updated.

**Service Worker Fix:**
```javascript
// In sw.js: version the cache name so old SW activates new cache on update
const CACHE_VERSION = 'v2'; // increment on every deploy
const CACHE_NAME = `app-cache-${CACHE_VERSION}`;

// In activate event: delete old caches
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
});
```

**CDN Fix:**
Use content-hashed asset filenames (`app.abc123.js`) so the URL changes on deploy.
Or: issue a CDN purge/invalidation as part of the deploy pipeline.

**How to confirm SW is the culprit:**
Open DevTools → Application → Service Workers.
If a service worker is registered and active, check its cache in Cache Storage.
If old assets appear in Cache Storage after deploy → SW cache is not being invalidated.

---

## CATEGORY 13 — VANILLA JS & DOM

### Pattern: addEventListener not firing — element not in DOM when listener attached
**Symptom:** Click/submit/input handler never executes. No error. The event fires (visible in DevTools Event Listeners tab) but the callback doesn't run.
**Why:** Script runs before the DOM element exists. `document.getElementById('btn')` returns `null`. Calling `.addEventListener()` on `null` throws silently in some contexts or is swallowed. Also: listener attached to the wrong element (parent instead of child, shadow DOM boundary).
**Prove:**
```javascript
const btn = document.getElementById('btn');
console.log('[DOM] btn element:', btn); // null = not in DOM yet
// If null → script runs before element. Wrap in DOMContentLoaded or move script to bottom.
```
**Fix:** Place script at bottom of `<body>`, or wrap in `document.addEventListener('DOMContentLoaded', () => { ... })`, or use `defer` attribute on `<script>`. Never call `.addEventListener()` without checking the element is non-null first.

### Pattern: Event delegation failing — e.target vs e.currentTarget confusion
**Symptom:** Listener attached to parent to catch events from dynamic children. Sometimes fires, sometimes doesn't. Fires for wrong element. Clicking exact icon/span inside button doesn't trigger.
**Why:** When a child element is clicked, `e.target` is the innermost clicked element (may be an icon `<svg>` or `<span>` inside the button). `e.currentTarget` is the element the listener is attached to. Comparing `e.target === btn` fails when user clicks a child of `btn`.
**Prove:**
```javascript
parent.addEventListener('click', e => {
  console.log('[EVENT] target:', e.target.tagName, e.target.className);
  console.log('[EVENT] currentTarget:', e.currentTarget.tagName);
  // If target is 'svg' or 'span' inside the button → closest() needed
});
```
**Fix:**
```javascript
parent.addEventListener('click', e => {
  const btn = e.target.closest('[data-action="submit"]'); // walk up to the button
  if (!btn) return; // click was outside any actionable element
  handleSubmit(btn.dataset);
});
```

### Pattern: `this` context lost in callback — regular function vs arrow function
**Symptom:** `this.someProperty` is `undefined` inside an event handler or setTimeout callback. Works when called directly, breaks when passed as callback.
**Why:** Regular functions bind `this` at call time. When passed as a callback, `this` becomes `undefined` (strict mode) or `window` (sloppy mode). Arrow functions capture `this` from the surrounding lexical scope at definition time.
**Prove:**
```javascript
class MyComponent {
  handleClick() {
    console.log('[THIS]', this); // undefined if called as plain callback
  }
  setup() {
    btn.addEventListener('click', this.handleClick); // WRONG — this is lost
    btn.addEventListener('click', () => this.handleClick()); // CORRECT — arrow preserves this
    btn.addEventListener('click', this.handleClick.bind(this)); // CORRECT — explicit bind
  }
}
```
**Fix:** Use arrow function wrapper or `.bind(this)` when passing class methods as callbacks. Or define the method as a class field arrow function: `handleClick = () => { ... }`.

### Pattern: async forEach doesn't await — loop completes before operations finish
**Symptom:** `forEach` loop over array with async operations. Code after the loop runs immediately. Operations appear to complete in wrong order or not at all. No error thrown.
**Why:** `Array.prototype.forEach` does not await the promise returned by an async callback. It fires all callbacks and returns immediately, regardless of whether the promises are resolved. This is by design — `forEach` was built before async/await.
**Prove:**
```javascript
const results = [];
// The bug: awaiting forEach itself is a no-op — forEach returns undefined,
// and `await undefined` completes instantly without waiting for any callbacks.
await [1, 2, 3].forEach(async (id) => {
  const data = await fetchById(id); // this await is inside the callback, not the outer scope
  results.push(data);
});
// Execution reaches here IMMEDIATELY — forEach launched all 3 fetches and returned undefined
console.log(results.length); // 0 — all fetches still in flight

// Confirm: log before and after forEach
console.log('[FOREACH] before forEach');
await arr.forEach(async item => { await doWork(item); });
console.log('[FOREACH] after forEach — if this prints before work completes → confirmed');
```
**Fix:**
```javascript
// Use for...of to await each iteration sequentially:
for (const id of ids) {
  const data = await fetchById(id);
  results.push(data);
}

// Or use Promise.all for parallel execution:
const results = await Promise.all(ids.map(id => fetchById(id)));
```

---

## CATEGORY 14 — PROMISE & ASYNC PATTERNS

### Pattern: fetch() doesn't throw on 4xx/5xx — error silently swallowed
**Symptom:** API call returns 400 or 500. JavaScript code continues as if the call succeeded. No error caught. Response body contains error message but it's never read.
**Why:** `fetch()` only rejects its promise on network failure (DNS, connection refused). HTTP error status codes (4xx, 5xx) resolve the promise successfully — `response.ok` is `false` but no exception is thrown. Code that only has `.catch()` for network errors silently ignores application errors.
**Prove:**
```javascript
const response = await fetch('/api/user');
console.log('[FETCH] ok:', response.ok);       // false for 4xx/5xx
console.log('[FETCH] status:', response.status); // 400, 404, 500, etc.
// If ok=false and no error thrown → missing ok check
```
**Fix:**
```javascript
const response = await fetch('/api/user');
if (!response.ok) {
  const errorBody = await response.text();
  throw new Error(`HTTP ${response.status}: ${errorBody}`);
}
const data = await response.json();
```

### Pattern: response.json() throws on empty body — 204 No Content crashes
**Symptom:** API call succeeds (confirmed in Network tab). `response.json()` throws `SyntaxError: Unexpected end of JSON input`. Only for certain endpoints (delete, update) that return 204.
**Why:** `response.json()` tries to parse the response body as JSON. A 204 No Content response has no body. `JSON.parse("")` throws a SyntaxError.
**Prove:** In Network tab, find the failing request. Check its response — if `Content-Length: 0` or no body → 204 pattern. `console.log('[FETCH] status:', response.status)` — if 204 → confirmed.
**Fix:**
```javascript
const response = await fetch('/api/item/123', { method: 'DELETE' });
if (response.status === 204 || response.headers.get('content-length') === '0') {
  return null; // no body to parse
}
const data = await response.json();
```

### Pattern: Promise.all fails fast — one rejection silently drops all others
**Symptom:** Loading several resources in parallel. One fails. Others also fail to load even though they succeeded. Or: one optional resource failing crashes the entire page.
**Why:** `Promise.all()` rejects immediately when ANY promise rejects, cancelling the wait for the others. Results from succeeded promises are discarded. If the operations are independent, this is almost always wrong.
**Prove:**
```javascript
const results = await Promise.all([fetchA(), fetchB(), fetchC()]);
// If fetchB() rejects, results from fetchA and fetchC are lost
// Add .catch() to each to see which one is actually failing:
const [a, b, c] = await Promise.all([
  fetchA().catch(e => ({ error: e })),
  fetchB().catch(e => ({ error: e })),
  fetchC().catch(e => ({ error: e })),
]);
console.log('[PARALLEL] results:', { a, b, c });
```
**Fix:**
```javascript
// For independent operations where partial success is acceptable:
const results = await Promise.allSettled([fetchA(), fetchB(), fetchC()]);
const succeeded = results.filter(r => r.status === 'fulfilled').map(r => r.value);
const failed = results.filter(r => r.status === 'rejected');
if (failed.length) console.error('[PARALLEL] some failed:', failed.map(f => f.reason));
```

### Pattern: Unhandled promise rejection — silent failure in production
**Symptom:** Feature stops working with no error visible to user. No console error in development. In production, error monitoring shows `UnhandledPromiseRejectionWarning` or `unhandledrejection` events.
**Why:** An async function throws or a `.then()` chain rejects without a `.catch()`. In development, browsers show a warning. In production, it silently fails. Node.js (older versions) exits the process. In modern browsers, the `unhandledrejection` event fires but code continues.
**Prove:**
```javascript
// Add globally to catch all unhandled rejections in development:
window.addEventListener('unhandledrejection', event => {
  console.error('[PROMISE] unhandled rejection:', event.reason);
  console.trace();
});
// This surfaces the exact promise and stack that was missing a .catch()
```
**Fix:** Every async function call must have either `await` inside a `try/catch`, or a `.catch()` at the end of the chain. For fire-and-forget operations that must not crash: `asyncFn().catch(err => logger.error(err))`.

---

## CATEGORY 15 — MODERN JS & TYPESCRIPT

### Pattern: Circular import — module sees `undefined` at import time
**Symptom:** Module A imports from Module B. Module B imports from Module A. One of the imported values is `undefined` at runtime even though it's clearly exported. No error at build time.
**Why:** ES module resolution handles circular imports by providing the binding, but if Module A has not finished executing when Module B first accesses its export, the value is `undefined` (it's a live binding that will be populated later, but by then the code that needed it has already run with `undefined`).
**Prove:**
```javascript
// In the module that sees undefined, add:
console.log('[CIRCULAR] imported value at module init:', importedValue);
// If undefined here but defined later → circular dependency confirmed

// Detect the cycle structurally — use madge (works for both ESM and CJS):
// npx madge --circular src/
// Output: Circular dependency found: moduleA.js → moduleB.js → moduleA.js

// Vite: vite-plugin-circular-dependency (NOT rollup-plugin-visualizer — that shows bundle size, not cycles)
// Webpack: circular-dependency-plugin
```
**Fix:** Break the cycle. Extract the shared value to a third module that neither A nor B imports from each other. Or restructure so one direction of the import is deferred (inside a function, not at top level).

### Pattern: TypeScript `as` type assertion hides null at runtime
**Symptom:** TypeScript compiles with no errors. Runtime crash: `Cannot read properties of undefined (reading 'name')`. The variable was typed as non-nullable but is actually null/undefined.
**Why:** `value as MyType` is a compile-time cast — it does NOT perform any runtime check or transformation. If `value` is actually `null` or `undefined`, the assertion makes TypeScript trust you that it isn't. The runtime doesn't care about TypeScript types.
**Prove:**
```typescript
const user = getUser() as User; // TypeScript satisfied
console.log('[TYPE] actual value:', user, typeof user); // may log undefined
user.name; // crashes if user is actually undefined
```
**Fix:**
```typescript
// Option 1 — runtime guard:
const user = getUser();
if (!user) throw new Error('getUser() returned null unexpectedly');
user.name; // TypeScript now knows it's non-null here

// Option 2 — optional chaining for nullable access:
const name = getUser()?.name ?? 'Unknown';

// Option 3 — use non-null assertion only when you are CERTAIN:
const user = getUser()!; // only if getUser() is guaranteed non-null in this code path
```
Rule: treat every `as` and `!` as a potential runtime crash site. Add a comment explaining WHY the assertion is safe.

### Pattern: Dynamic import() chunk missing after deploy — 404 on lazy-loaded route
**Symptom:** App works. New version deployed. Some users (those with the app already open) get a blank page or error when navigating to a lazy-loaded route. Error: `Failed to load resource: net::ERR_ABORTED 404` for a `.js` chunk URL. New visitors are unaffected. Hard refresh fixes it for the affected user.
**Why:** Bundlers (Vite, webpack, Rollup) emit code-split chunks with content-hashed filenames (`chunk.Bq7mKpRx.js`). On deploy, old hashed files are replaced with new ones (`chunk.Cx9nLwTy.js`). A user who loaded the app *before* the deploy still has the old HTML in memory referencing the old hash. The next `React.lazy()` / dynamic `import()` triggered by navigation fetches the old URL — 404. `<Suspense>` has no `fallback` for module load errors, so the route renders blank. Only pre-deploy users are affected, which is exactly why the alternative explanation "the CDN is broken" is wrong: new visitors work fine.
**Prove:** Open Network tab during the failure. The failing request is a `.js` chunk with a hash in the name. Compare to what's on the CDN — old hash gone, new hash present. Only pre-deploy sessions reproduce; an incognito window works.
**Fix:** Two parts. **Both are needed for a complete one-shot fix.**

**(1) Client — React Router 6 `errorElement` catches the chunk load failure and forces ONE guarded reload:**
```jsx
// router.tsx — React Router 6 / 6.4+ data router
import { createBrowserRouter, useRouteError } from 'react-router-dom';

function ChunkErrorBoundary() {
  const error = useRouteError() as Error;
  const isChunkError =
    /Failed to fetch dynamically imported module/.test(error?.message ?? '') ||
    /Importing a module script failed/.test(error?.message ?? '') ||
    /ChunkLoadError/.test(error?.name ?? '');

  if (!isChunkError) {
    return <GenericErrorUI error={error} />;
  }

  // Guard: only reload ONCE per session — prevents infinite reload loop if CDN is actually down
  const alreadyReloaded = sessionStorage.getItem('chunk_reload_attempted');
  if (alreadyReloaded) {
    console.error('[CHUNK] reload did not fix chunk error — CDN may be down');
    return <GenericErrorUI error={error} />;
  }
  sessionStorage.setItem('chunk_reload_attempted', '1');
  window.location.reload(); // fetches fresh HTML referencing the NEW chunk hashes
  return null;
}

const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    errorElement: <ChunkErrorBoundary />, // catches lazy() module load failures
    children: [
      { path: 'settings', element: <SettingsLazy /> }, // React.lazy(() => import('./Settings'))
    ],
  },
]);

// Clear the guard once the user successfully navigates after reload — so a *future*
// chunk error in the same session can also self-heal:
window.addEventListener('load', () => sessionStorage.removeItem('chunk_reload_attempted'));
```

**(2) Server / CDN — keep old chunks alive for 1–2 hours after deploy** so in-flight users finish their session without ever hitting a 404. Configure your deploy pipeline to *add* new hashed files rather than *replace* the directory, and run a janitor that prunes files older than ~2 hours. This converts the chunk-404 from a hard error into a non-event for almost all users; the `errorElement` reload is the safety net for the rest.

**Do NOT:** disable content hashing (breaks long-term CDN caching), wrap `<Suspense>` in a plain `ErrorBoundary` without auto-reload (user has to manually refresh), or increase CDN TTL (wrong direction — the problem is files being *deleted*, not over-cached).
