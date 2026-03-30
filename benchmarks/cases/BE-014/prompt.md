# BE-014: Session Data Lost Between Requests With In-Memory Store

## User Prompt

Users get randomly logged out in production. It does not happen consistently. The session setup looks correct. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, express-session 1.17, 2 instances
- environment: production with 2 app instances
- logs:
- users report random logouts
  - session data missing on requests hitting the second instance
  - console warning: 'express-session: MemoryStore is not designed for a production environment'
- code excerpt:
```js
app.use(session({ secret: 'secret', resave: false }))
// No store configured — uses MemoryStore by default
```
- reproduction:
1. Log in (hits instance A)
2. Next request hits instance B
3. User is logged out — session not found
