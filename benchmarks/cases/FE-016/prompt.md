# FE-016: localStorage Access Throws In Private Browsing Mode

## User Prompt

Users in Safari private browsing get a crash on login. The error is SecurityError on localStorage. Chrome incognito works fine. What is the bug?

## Context Provided To The Skill

- stack: React 18.2, TypeScript 5.0
- environment: Safari Private Browsing
- logs:
- SecurityError: The operation is insecure
  - thrown on localStorage.setItem()
  - only occurs in Safari private browsing
  - Chrome incognito works fine
- code excerpt:
```js
localStorage.setItem('user', JSON.stringify(userData))
```
- reproduction:
1. Open Safari in private browsing
2. Log in
3. Observe SecurityError on localStorage write
