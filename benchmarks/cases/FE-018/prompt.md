# FE-018: Infinite Render Loop From Incorrect useEffect Dependency

## User Prompt

Our page freezes immediately on load. React DevTools shows infinite re-renders. The useEffect has options in the dependency array. What is the bug?

## Context Provided To The Skill

- stack: React 18.2, TypeScript 5.0
- environment: browser
- logs:
- browser tab freezes immediately on page load
  - Chrome shows 'Aw, Snap!' after a few seconds
  - React DevTools shows thousands of renders per second
- code excerpt:
```jsx
const options = { page: 1, limit: 10 }
useEffect(() => {
  fetchData(options)
}, [options])
```
- reproduction:
1. Load the page
2. Browser freezes within 1-2 seconds
