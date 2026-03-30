# FE-003: Route Param Changes But Component Does Not Re-Fetch

## User Prompt

When navigating between user profile pages the old user's data stays on screen until hard refresh. The URL changes correctly. What is the bug?

## Context Provided To The Skill

- stack: React 18.2, React Router 6.11, TypeScript 5.0
- environment: browser SPA
- logs:
- navigating /user/1 then /user/2 still shows user 1 data
  - hard refresh on /user/2 shows correct user 2 data
  - no fetch call visible in network tab on param change
- code excerpt:
```jsx
useEffect(() => {
  fetchUser(userId).then(setUser)
}, [])
```
- reproduction:
1. Navigate to /user/1 — loads correctly
2. Click link to /user/2
3. Observe user 1 data still displayed
