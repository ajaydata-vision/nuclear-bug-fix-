# FE-019: Stale Service Worker Serves Old Assets After Deploy

## User Prompt

We deployed a frontend fix, CI passed, the new bundle is in the release, but
some users still see the old broken JavaScript until they hard refresh. API and
HTML are definitely updated. Why is the fix not actually live for everyone?

## Context Provided To The Skill

- stack: React 18.2.0 + Workbox service worker
- versions: Chrome 123, Safari 17
- environment: production app behind CDN
- logs:
  - HTML references `app.91d2.js`
  - affected clients still request cached `app.74ab.js`
  - hard refresh resolves the issue immediately
- code excerpt:

```js
self.addEventListener('fetch', event => {
  event.respondWith(caches.match(event.request).then(r => r || fetch(event.request)));
});
```

- reproduction:
  1. Load version N of the site
  2. Deploy version N+1
  3. Reopen the app without hard refresh
  4. Observe old behavior persists
