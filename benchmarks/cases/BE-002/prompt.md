# BE-002: Valid Route Returns 404 Because Catch-All Mounted Too Early

## User Prompt

A specific API route returns 404 even though it is defined in our Express app. Other routes work. What is the real bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2
- environment: development and production
- logs:
- GET /api/users returns 404
  - route /api/users is defined
  - other routes work correctly
  - catch-all handler returns 404 for all unmatched routes
- code excerpt:
```js
app.use((req, res) => res.status(404).json({ error: 'Not found' }))
app.get('/api/users', (req, res) => res.json(users))
```
- reproduction:
1. GET /api/users
2. Observe 404 instead of users list
