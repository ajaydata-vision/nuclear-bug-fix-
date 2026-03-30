# RC-011: Session Fixation From Concurrent Login Requests

## User Prompt

Users occasionally get wrong session data when our login endpoint receives concurrent requests. This is a security concern. What is the root cause?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, express-session 1.17, Redis
- environment: production under concurrent load
- logs:
- concurrent login requests from same user
  - user ends up with wrong session data
  - session from first request overwritten by second before response sent
  - req.session.userId wrong in one of the concurrent responses
- code excerpt:
```js
app.post('/login', async (req, res) => {
  const user = await authenticate(req.body)
  req.session.userId = user.id  // race: two requests sharing a session
  req.session.save()
  res.json({ token: user.token })
})
```
- reproduction:
1. Send two concurrent login requests from the same client
2. Both modify the same session
3. One request's userId is overwritten by the other
