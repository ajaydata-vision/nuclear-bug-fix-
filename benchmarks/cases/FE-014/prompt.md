# FE-014: Safari-Only Failure Due to Unsupported Browser API

## User Prompt

Our input validation crashes in Safari but works in Chrome and Firefox. The error mentions a regular expression group. What is the real cause?

## Context Provided To The Skill

- stack: React 18.2, TypeScript 5.0
- environment: Safari 16.x (macOS and iOS)
- logs:
- TypeError: Invalid regular expression: invalid group specifier name (Safari)
  - works in Chrome 120 and Firefox 121
  - error thrown in validation function
- code excerpt:
```js
const pattern = /(?<=@)\w+/  // lookbehind assertion
```
- reproduction:
1. Load the page in Safari
2. Trigger the validation containing the regex
3. Observe TypeError
