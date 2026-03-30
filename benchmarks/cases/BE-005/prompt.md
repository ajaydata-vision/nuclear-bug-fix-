# BE-005: Token Valid In Postman But Rejected In App Due To Malformed Bearer Prefix

## User Prompt

Our auth token works in Postman but is rejected in the app. The backend team says the token is valid. What is the actual bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, JWT
- environment: browser to API
- logs:
- 401 Unauthorized in app
  - same token works in Postman
  - Authorization header in app: 'BearereyJhbGci...' (no space)
  - Authorization header in Postman: 'Bearer eyJhbGci...' (correct)
- code excerpt:
```js
headers: {
  'Authorization': 'Bearer' + token  // missing space
}
```
- reproduction:
1. Log in and get token
2. Make authenticated request from app
3. Observe 401 while Postman with same token succeeds
