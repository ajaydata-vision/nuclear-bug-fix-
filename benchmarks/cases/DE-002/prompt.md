# DE-002: CDN Still Serves Old JavaScript After Deploy

## User Prompt

We deployed a frontend fix and the origin is updated, but some users still load
the old broken JavaScript for several minutes. If they bypass the CDN, the fix
is there immediately. What is the real problem?

## Context Provided To The Skill

- stack: static frontend behind CDN
- versions: hashed HTML disabled, bundle path is `/assets/app.js`
- environment: production deploy
- logs:
  - origin serves new `app.js`
  - CDN edge still serves old `app.js`
  - cache-control on bundle is `public, max-age=3600`
- config excerpt:

```http
Cache-Control: public, max-age=3600
```

- reproduction:
  1. Deploy new frontend bundle to origin
  2. Load app through CDN
  3. Observe old JS until cache expires or is purged
