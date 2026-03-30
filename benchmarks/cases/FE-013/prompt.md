# FE-013: Query Params Silently Dropped During Router Navigation

## User Prompt

Programmatic navigation drops all query parameters from the URL. The search and pagination state is lost on every navigation. What is the bug?

## Context Provided To The Skill

- stack: React 18.2, React Router 6.11
- environment: browser SPA
- logs:
- URL before navigation: /search?q=test&page=2
  - URL after navigation: /search
  - query params absent after programmatic navigation
- code excerpt:
```js
navigate('/search')
```
- reproduction:
1. Load /search?q=test&page=2
2. Trigger the navigation action
3. Observe URL becomes /search with no params
