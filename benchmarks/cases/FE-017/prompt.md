# FE-017: Page Slows Over Time Due To Event Listeners Never Cleaned Up

## User Prompt

Our app gets slower the longer a user stays on it. Performance degrades noticeably after navigating between routes multiple times. What is causing the leak?

## Context Provided To The Skill

- stack: React 18.2, TypeScript 5.0
- environment: browser, long-running SPA session
- logs:
- performance degrades after navigating between routes multiple times
  - Chrome DevTools memory panel shows growing event listener count
  - CPU usage increases over time
- code excerpt:
```jsx
useEffect(() => {
  window.addEventListener('resize', handleResize)
}, [])
```
- reproduction:
1. Navigate between routes 10 times
2. Check Chrome DevTools event listeners panel
3. Observe resize listener count growing with each navigation
