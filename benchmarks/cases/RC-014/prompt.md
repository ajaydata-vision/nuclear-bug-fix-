# RC-014: setState Called After Component Unmount Causes Memory Leak Warning

## User Prompt

We get a React warning about setState on an unmounted component when users navigate away during a slow API call. How do we properly fix this?

## Context Provided To The Skill

- stack: React 17.0.2, TypeScript 5.0
- environment: browser SPA
- logs:
  - Warning: Can't perform a React state update on an unmounted component
  - occurs when navigating away from a page during a slow fetch
  - not reproducible on fast connections
  - no visible crash; warning only, but memory leak confirmed in DevTools
- code excerpt:
```jsx
useEffect(() => {
  fetchUserData(userId).then(data => {
    setUser(data)  // may run after unmount
  })
}, [userId])
// No cleanup / no AbortController
```
- reproduction:
1. Navigate to user profile page (triggers fetch)
2. Immediately navigate away before fetch completes
3. Observe React warning in console
