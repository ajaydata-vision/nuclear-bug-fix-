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
**Fix:** Ensure server and client produce identical output. Defer browser-only code to after hydration. Use `suppressHydrationWarning` only as last resort.

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
**Symptom:** Smooth in dev. Jank/stutter in prod or on low-end device.
**Why:** Layout thrashing (read then write DOM in loop). Expensive computation on main thread. Non-GPU-accelerated CSS properties being animated.
**Prove:** Open DevTools Performance tab. Record the jank. Look for long tasks and layout events.
**Fix:** Use `transform` and `opacity` for animations (GPU-accelerated). Move computation to Web Worker. Batch DOM reads/writes with `requestAnimationFrame`.
