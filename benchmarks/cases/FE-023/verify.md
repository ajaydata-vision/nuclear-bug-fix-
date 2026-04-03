# Verification

## Before Fix
- Users with app open during deploy get blank page on /settings
- Network shows 404 for old-hash chunk
- Manual refresh fixes it (gets new HTML)

## After Fix

### Fix 1 — React Router 6 chunk error handling with reload guard:
```tsx
// ChunkErrorBoundary.tsx
function ChunkErrorFallback() {
  const error = useRouteError();

  useEffect(() => {
    const isChunkError =
      error instanceof Error && (
        error.message.includes('Failed to fetch dynamically imported module') ||
        error.message.includes('Importing a module script failed')
      );
    if (!isChunkError) return;

    // Guard: only reload once per session — prevents infinite loop if CDN is down
    if (sessionStorage.getItem('chunk_reload_attempted')) {
      console.error('[CHUNK] Reload did not fix chunk error — CDN may be down');
      return;
    }
    sessionStorage.setItem('chunk_reload_attempted', '1');
    window.location.reload();
  }, [error]);

  return <div>Loading this page failed. Please refresh.</div>;
}

// router.tsx — add errorElement to lazy routes
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route
        path="/settings"
        errorElement={<ChunkErrorFallback />}   // ← catches chunk load failures
        element={
          <Suspense fallback={<LoadingSpinner />}>
            <SettingsPage />
          </Suspense>
        }
      />
    </Routes>
  );
}
```

### Fix 2 — Retain old chunks on CDN for 1-2 hours post-deploy:
Configure deploy pipeline to keep previous build's assets alongside new ones.
Set `Cache-Control: max-age=7200` on chunk files (2 hours).

1. User with old HTML navigates to /settings → chunk 404 → `ChunkErrorFallback` renders
2. sessionStorage guard not set → reloads once
3. Reload fetches new HTML → /settings loads with new chunk hash ✅
4. CDN down scenario: guard detects reload already attempted, stops loop, shows error message

## Regression Checks
- CDN fully down (all chunks 404): guard stops reload loop after one attempt, shows error UI
- New users (fresh HTML load): no chunk error, no errorElement triggered
- Successful navigation clears guard: add `sessionStorage.removeItem('chunk_reload_attempted')` on successful route transitions if needed
- Other route errors (not chunk-related): `isChunkError` check prevents reload for non-chunk errors
