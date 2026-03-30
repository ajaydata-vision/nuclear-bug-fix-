# BE-006: Login Works But Next Request Fails Because Cookie Domain Mismatch

## User Prompt

Users can log in but are immediately unauthenticated on the next request. The session cookie is set after login but not sent on subsequent requests. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, express-session
- environment: frontend on app.example.com, API on api.example.com
- logs:
- POST /login returns 200 and Set-Cookie header
  - subsequent GET /profile returns 401
  - browser does not send session cookie with /profile request
  - Set-Cookie shows Domain=api.example.com, SameSite=Strict
- code excerpt:
```js
app.use(session({
  secret: 'secret',
  cookie: { sameSite: 'strict', domain: 'api.example.com' }
}))
```
- reproduction:
1. POST /login → 200, cookie set
2. GET /profile → 401, no cookie sent
