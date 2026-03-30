# Benchmark Backlog

This backlog is a curated list of benchmark cases worth adding first.

## Frontend

- `FE-001` SSR hydration mismatch caused by `Date.now()` in rendered output
- `FE-002` stale closure loses rapid counter increments in React state updates
- `FE-003` route parameter changes but component does not re-fetch
- `FE-004` CSS purge removes dynamic classes in production only
- `FE-005` stacking context hides modal despite high z-index
- `FE-006` form submit handler never reached because wrong binding is used
- `FE-007` frontend validation passes but serialized payload fails backend validation
- `FE-008` two concurrent fetches race and late empty response overwrites good data
- `FE-009` websocket connects before `onmessage` handler is attached
- `FE-010` reconnect loop caused by auth close code ignored by client
- `FE-011` production bundle breaks because env var lacks `VITE_` prefix
- `FE-012` SPA refresh returns 404 because server does not route to `index.html`
- `FE-013` query params silently dropped during router navigation
- `FE-014` Safari-only failure due unsupported browser API
- `FE-015` CORS preflight fails with credentials mode mismatch
- `FE-016` localStorage fails in private browsing mode without fallback
- `FE-017` page slows over time due event listeners never cleaned up
- `FE-018` infinite render loop from incorrect effect dependency
- `FE-019` stale service worker serves old assets after deploy
- `FE-020` Chrome works, Firefox fails due date parsing assumption

## Backend

- `BE-001` request body undefined because body parser order is wrong
- `BE-002` valid route returns 404 due catch-all route mounted too early
- `BE-003` duplicate write caused by client retry and missing idempotency key
- `BE-004` timeout returned to client even though operation completed server-side
- `BE-005` token valid in Postman but rejected in app because `Bearer ` prefix is malformed
- `BE-006` login works but next request fails due `SameSite` or domain cookie mismatch
- `BE-007` ORM query returns wrong rows because generated SQL join is incorrect
- `BE-008` migration ran successfully on the wrong database
- `BE-009` unique constraint race under concurrent inserts
- `BE-010` background job consumed and disappears because error is swallowed
- `BE-011` cron runs at wrong time because server timezone is not UTC
- `BE-012` uploaded file stored on local disk is inaccessible in multi-instance deployment
- `BE-013` large file upload fails due proxy size limit instead of app limit
- `BE-014` session data lost between requests because store is in-memory
- `BE-015` session leaks between users due module-level mutable state
- `BE-016` legitimate users hit rate limit because proxy IP is used as key
- `BE-017` logs appear clean because exceptions are logged only at debug level
- `BE-018` external API works in dev and fails in prod due outbound firewall rules
- `BE-019` stale cache returned after write because invalidation never happens
- `BE-020` read-after-write inconsistency caused by replica lag

## Integration And Pipeline

- `IN-001` webhook never arrives because external service still points to old URL
- `IN-002` webhook signature validation fails because raw body is not preserved
- `IN-003` webhook processed twice because retries are not deduplicated
- `IN-004` queue consumer listens on wrong topic name
- `IN-005` message acknowledged before processing and silently lost on handler failure
- `IN-006` consumer lag grows because one DB query inside handler is the bottleneck
- `IN-007` duplicate message processing caused by at-least-once delivery semantics
- `IN-008` downstream service returns 200 but schema drift breaks caller assumptions
- `IN-009` cascading failure because no timeout or circuit breaker is configured
- `IN-010` service discovery resolves wrong instance because DNS cache is stale
- `IN-011` ETL silently drops final batch because flush never happens
- `IN-012` ETL values wrong due timezone conversion during transform
- `IN-013` month-boundary pipeline fails due off-by-one date range
- `IN-014` incremental pipeline reprocesses old data because checkpoint precision is wrong
- `IN-015` schema change silently breaks pipeline mapping
- `IN-016` CI passes but prod fails because tests use mocks instead of real dependency behavior
- `IN-017` deploy succeeds but old image is still running in cluster
- `IN-018` missing env var in deploy target causes runtime failure after successful CI
- `IN-019` gateway strips auth header before request reaches service
- `IN-020` mTLS mesh breaks service-to-service calls because sidecar or cert is wrong

## Mobile

- `MO-001` React Native native module is null because linking or pods are incomplete
- `MO-002` feature works on Android and fails on iOS due platform-specific API behavior
- `MO-003` Android ANR caused by heavy work on main thread
- `MO-004` push notification never reaches device because token is stale
- `MO-005` offline changes never sync because reconnect does not trigger queue flush
- `MO-006` app killed on older device due memory growth from image-heavy list
- `MO-007` camera or notification permission missing on one platform only
- `MO-008` deep link opens app but wrong screen due route mapping mismatch
- `MO-009` background refresh disabled causes delayed sync behavior
- `MO-010` websocket reconnect loop drains battery on unstable networks
- `MO-011` secure storage value lost after reinstall or biometric state change
- `MO-012` cold-start notification tap handler races app initialization
- `MO-013` RN New Architecture mismatch breaks native bridge module
- `MO-014` app state transition causes pending update to be dropped
- `MO-015` date parsing differs between iOS and Android locale settings

## Intermittent And Race

- `RC-001` shared counter loses increments under concurrent access
- `RC-002` inventory oversell caused by TOCTOU check-then-update logic
- `RC-003` singleton or cache object used before initialization completes
- `RC-004` async result consumed before awaited operation finishes
- `RC-005` callback captures stale state and applies wrong update
- `RC-006` duplicate distributed processing because dedupe check is not atomic
- `RC-007` connection pool exhaustion appears only under burst load
- `RC-008` flaky test passes alone and fails under randomized test order
- `RC-009` startup race between app boot and migration or cache warmup
- `RC-010` cache stampede causes duplicate expensive recomputations
- `RC-011` scheduled job runs twice in multi-instance deployment
- `RC-012` concurrent file writes truncate or corrupt content
- `RC-013` optimistic locking missing version guard causes lost update
- `RC-014` broker redelivery after worker crash before ack causes duplicate side effect
- `RC-015` asyncio shared mutable state race in Python service
- `RC-016` browser tabs race on localStorage write order
- `RC-017` load balancer retry causes duplicate charge or email
- `RC-018` readiness probe passes before true dependency readiness
- `RC-019` websocket event arrives before listener registration
- `RC-020` race appears only when external service latency increases

## Version And External Intelligence

- `VE-001` framework major upgrade changed API behavior and broke old assumption
- `VE-002` browser release changed cookie or `SameSite` semantics
- `VE-003` library has confirmed bug in exact version used by the app
- `VE-004` runtime version is below framework minimum requirement
- `VE-005` plugin version is incompatible with core framework version
- `VE-006` protocol implementation violates HTTP or OAuth RFC requirements
- `VE-007` JWT validation bug caused by wrong algorithm assumption
- `VE-008` CSS feature has partial support and fails on target browser
- `VE-009` package advisory or CVE explains auth or TLS failure
- `VE-010` WebSocket upgrade headers are invalid through reverse proxy
- `VE-011` SMTP integration fails due line ending or auth protocol mismatch
- `VE-012` timezone parsing bug caused by RFC3339 vs local-format mismatch
- `VE-013` framework changelog documents the exact regression introduced after upgrade
- `VE-014` MDN or caniuse compatibility table contradicts frontend assumption
- `VE-015` ORM driver mismatch causes subtle runtime query failures

## Deploy And Environment

- `DE-001` fixed code never runs because old container image is still deployed
- `DE-002` CDN serves stale JavaScript bundle after successful deploy
- `DE-003` wrong `.env` file loaded in staging
- `DE-004` relative file path resolves differently in worker vs web process
- `DE-005` log sink inspected by engineer is not the sink used by failing service
- `DE-006` one instance in pool is old version and receives only some traffic
- `DE-007` blue-green deploy never switched traffic to new environment
- `DE-008` reverse proxy timeout masks successful long-running server operation
- `DE-009` secret rotated in one service but not dependent service
- `DE-010` staging reproduces issue only with production data volume, not synthetic data

