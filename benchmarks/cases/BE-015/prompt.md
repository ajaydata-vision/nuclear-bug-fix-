# BE-015: Session Data Leaks Between Users Via Module-Level Mutable State

## User Prompt

Users occasionally see each other's data under load. We cannot reproduce it consistently. It is being treated as a security incident. What is the real bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2
- environment: production, concurrent traffic
- logs:
- users occasionally see another user's data
  - only happens under concurrent load
  - single-user load testing shows no issue
  - security incident reported
- code excerpt:
```js
let currentUser = null  // module-level variable

app.get('/profile', async (req, res) => {
  currentUser = await getUser(req.session.userId)
  res.json(currentUser)
})
```
- reproduction:
1. Two concurrent requests from different users
2. Observe user A sometimes gets user B's profile
