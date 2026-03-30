# FE-002: Stale Closure Loses Rapid Counter Increments

## User Prompt

Our click counter falls behind when users click rapidly. Five fast clicks only increment the count by one. No errors shown. What is the real bug?

## Context Provided To The Skill

- stack: React 18.2.0, TypeScript 5.0, Vite 5.0
- environment: browser, development and production
- logs:
- counter value jumps from 0 to 1 then resets
  - rapid clicks produce final count lower than click count
  - no errors in console
- code excerpt:
```jsx
const [count, setCount] = useState(0)
const handleClick = () => {
  setTimeout(() => {
    setCount(count + 1)
  }, 100)
}
```
- reproduction:
1. Click the button rapidly 5 times
2. Wait for timeouts to resolve
3. Observe count is 1, not 5
