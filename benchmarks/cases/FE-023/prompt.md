# FE-023: Lazy-Loaded Route Shows Blank Page For Some Users After Deploy

## User Prompt

We deployed a new version of our React app. Most users are fine. But users who had
the app open in a tab during the deploy get a blank white page when they navigate
to the Settings route. Refreshing the page fixes it immediately. The error only
affects users who were already using the app when we deployed. New visitors are
fine. What is causing this?

## Context Provided To The Skill

- stack: React 18.2.0, React Router 6.22, Vite 5.1, TypeScript 5.3
- versions: Node.js 20.11, deployed to Nginx + CDN (Cloudflare)
- environment: production, affects only users with app open during deploy
- logs:
  - Browser console: `Failed to fetch dynamically imported module: https://app.example.com/assets/SettingsPage.Bq7mKpRx.js`
  - Network tab: GET `/assets/SettingsPage.Bq7mKpRx.js` → 404
  - After deploy, CDN serves: `/assets/SettingsPage.Cx9nLwTy.js` (new hash)
- code excerpt:
```typescript
// router.tsx — Settings is lazy-loaded
const SettingsPage = lazy(() => import('./pages/SettingsPage'));

export function AppRouter() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route
        path="/settings"
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
- reproduction:
  1. User opens app, loads `/` (gets old HTML with reference to `SettingsPage.Bq7mKpRx.js`)
  2. New version deployed — `SettingsPage.Bq7mKpRx.js` deleted from CDN, replaced with `SettingsPage.Cx9nLwTy.js`
  3. User navigates to `/settings` — browser tries to fetch `SettingsPage.Bq7mKpRx.js`
  4. CDN returns 404 (old file gone) → blank page
  5. User refreshes → gets new HTML → loads `SettingsPage.Cx9nLwTy.js` → works
