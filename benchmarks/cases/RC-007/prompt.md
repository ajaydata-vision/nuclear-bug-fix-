# RC-007: Thread-Local Storage Contamination Leaks Request Data Between Users

## User Prompt

User IDs are leaking between requests in our logging system. Under load we see one user's ID appearing in logs for another user's request. This is a security concern. What is the real bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, cls-hooked 4.2
- environment: production under concurrent load
- logs:
- users occasionally see each other's user IDs in logs
  - request context contains wrong userId under load
  - context set correctly at request start
  - async callback resolves in different request context
- code excerpt:
```js
const namespace = cls.createNamespace('request')
app.use((req, res, next) => {
  namespace.set('userId', req.user.id)
  next()  // context may bleed into other requests
})
```
- reproduction:
1. Send concurrent requests from different users
2. Log the CLS namespace userId in an async callback
3. Observe wrong userId appearing under load
