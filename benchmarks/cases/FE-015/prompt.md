# FE-015: CORS Preflight Fails With Credentials Mode Mismatch

## User Prompt

Our cross-origin fetch with credentials fails with a CORS error about wildcard origin. The backend allows all origins. What is actually wrong?

## Context Provided To The Skill

- stack: React 18.2, Express 4.18, Node.js 20
- environment: cross-origin browser to API
- logs:
- CORS error: 'The value of the Access-Control-Allow-Origin header must not be the wildcard * when the request credentials mode is include'
  - OPTIONS preflight returns Access-Control-Allow-Origin: *
  - fetch uses credentials: include
- code excerpt:
```js
// Frontend
fetch(API_URL, { credentials: 'include' })

// Backend
app.use(cors({ origin: '*' }))
```
- reproduction:
1. Make authenticated fetch request cross-origin
2. Observe CORS error in console
3. Preflight returns wildcard origin
