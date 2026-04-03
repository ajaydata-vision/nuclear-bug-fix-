# Evaluator

## Metadata

- id: FE-023
- domain: frontend
- track: deploy-env
- difficulty: medium
- determinism: deterministic
- one_shot_eligible: true
- requires_external_intelligence: false
- requires_runtime_access: false
- requires_log_access: true
- tags: vite, react, lazy-loading, dynamic-import, chunk, deploy, cdn, 404

## Ground Truth

- root_cause: Content-hashed chunk filenames change on every build. The user's browser holds old HTML (loaded before deploy) that references the old chunk hash `Bq7mKpRx`. After deploy, only the new hash `Cx9nLwTy` exists on the CDN. When the user navigates to Settings, `React.lazy()` triggers a dynamic `import()` of the old URL, which returns 404. `Suspense` catches the module load failure and renders nothing (blank page).
- why_it_happens: Vite generates content-hashed filenames to enable long-term CDN caching. On deploy, old files are replaced with new ones. Users who loaded the app before deploy have stale HTML in memory referencing old chunk URLs. The next navigation to a lazy route triggers a fetch of an URL that no longer exists. Without a chunk load error handler, the failure is silent — `Suspense` has no fallback for load errors, rendering blank.
- accepted_fix: Two parts: (1) Add a React Router 6 `errorElement` to catch chunk load failures and trigger a guarded reload — using `sessionStorage` to prevent infinite reload loops if CDN is down. (2) Retain old chunk files on CDN for 1-2 hours after deploy to allow in-flight users to complete their sessions without 404s.
- rejected_fix_patterns:
  - disable content hashing in Vite build (breaks long-term caching)
  - add an ErrorBoundary around Suspense without also triggering a reload (shows error UI but user must manually refresh)
  - increase CDN TTL (opposite direction — problem is old files being deleted, not cached too long)

## Evidence Signals

- strongest_signal: Network tab shows 404 for a chunk URL with old hash; new hash exists on CDN; only affects users who had app open before deploy; refresh fixes it immediately
- strongest_alternative_explanation: A CDN misconfiguration is serving 404 for all assets, not just the old-hash chunk
- why_alternative_is_wrong: New visitors work correctly (they get the new HTML and new chunk hash). Only users with old HTML in memory are affected. A CDN misconfiguration would affect all users including new ones. The 404 is specific to one old-hash URL, not a systemic CDN failure.

## Scoring Notes

- full_credit_conditions:
  - identifies stale chunk reference in old HTML as root cause
  - explains content-hashing mechanism and why old chunks are deleted on deploy
  - prescribes chunk load error handler with reload (with guard against infinite reload loops)
  - mentions retaining old chunks on CDN as a complementary strategy
- partial_credit_conditions:
  - correctly diagnoses the problem and prescribes a reload on error without mentioning the sessionStorage guard against infinite loops
  - identifies root cause but only suggests ErrorBoundary without automatic reload
- fail_conditions:
  - recommends disabling content hashing
  - blames CDN misconfiguration
  - suggests increasing CDN TTL as the fix
