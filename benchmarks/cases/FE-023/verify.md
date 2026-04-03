# Verification

## Before Fix
- Users with app open during deploy get blank page on /settings
- Network shows 404 for old-hash chunk
- Manual refresh fixes it (gets new HTML)

## After Fix

### Fix 1 — Chunk load error handler with reload guard:
```typescript
// main.tsx or router setup
router.onError((error: Error) => {
  const isChunkError =
    error.message.includes('Failed to fetch dynamically imported module') ||
    error.message.includes('Importing a module script failed') ||
    error.name === 'ChunkLoadError';

  if (!isChunkError) return;

  // Guard: only reload once per session — prevents infinite loop if CDN is down
  if (sessionStorage.getItem('chunk_reload_attempted')) {
    console.error('[CHUNK] Reload failed — CDN may be unavailable');
    return; // show error UI instead of looping
  }
  sessionStorage.setItem('chunk_reload_attempted', '1');
  window.location.reload();
});

// Clear guard on successful navigation
router.afterEach(() => {
  sessionStorage.removeItem('chunk_reload_attempted');
});
```

### Fix 2 — Retain old chunks on CDN for 1-2 hours post-deploy:
Configure deploy pipeline to keep previous build's assets alongside new ones.
Nginx/Cloudflare: set `Cache-Control: max-age=7200` on chunk files (2 hours).

1. User with old HTML navigates to /settings → chunk load error handler fires
2. sessionStorage guard not set → reloads once
3. Reload fetches new HTML with new chunk hash → /settings loads correctly
4. sessionStorage guard cleared by afterEach on successful navigation

## Regression Checks
- CDN down (all chunks 404): handler detects reload already attempted, stops loop, shows error UI
- New users (fresh load): no chunk error, no reload
- Multiple lazy routes: each route's 404 triggers one reload; guard resets after success
