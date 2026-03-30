# FE-008: Late Empty Response Overwrites Good Data

## User Prompt

Our search screen loads results, then sometimes clears them a moment later.
The API is fine when called directly. We only see this in the UI when users
type quickly. What is the real bug?

## Context Provided To The Skill

- stack: React 18.2.0 + Vite 5.2.8
- versions: Node.js 20.10.0
- environment: browser app against a stable search API
- logs:
  - request A `/search?q=ap` returns 8 results in 120ms
  - request B `/search?q=app` returns `[]` in 480ms
  - UI briefly shows 8 results, then becomes empty
- code excerpt:

```tsx
useEffect(() => {
  fetch(`/search?q=${query}`)
    .then(r => r.json())
    .then(setResults);
}, [query]);
```

- reproduction:
  1. Type `a`, then `ap`, then `app` quickly
  2. Observe correct results appear briefly
  3. Observe empty state overwrite them later
