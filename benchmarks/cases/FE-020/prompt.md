# FE-020: Chrome Works But Firefox Fails Due To Date Parsing Assumption

## User Prompt

Dates display correctly in Chrome but show 'Invalid Date' in Firefox. The API returns dates in a specific format. What is the bug?

## Context Provided To The Skill

- stack: React 18.2, TypeScript 5.0
- environment: Firefox 121 (fails), Chrome 120 (works)
- logs:
- Invalid Date shown in Firefox for all dates
  - same code works in Chrome
  - date string from API: '2024-01-15 09:30:00' (no T separator)
- code excerpt:
```js
const date = new Date('2024-01-15 09:30:00')
console.log(date.toLocaleDateString())
```
- reproduction:
1. Open in Firefox
2. Observe 'Invalid Date' displayed
3. Open same page in Chrome and observe correct date
