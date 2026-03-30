# IN-008: Downstream Service Returns 200 But Schema Drift Breaks Caller

## User Prompt

Our service started crashing after a downstream team deployed what they called a non-breaking change. We get a TypeError accessing a field that exists in our code. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, axios 1.6
- environment: production after downstream service deployment
- logs:
- TypeError: Cannot read properties of undefined (reading 'id')
  - error in caller code accessing response.data.user.id
  - downstream service returns 200
  - response body changed: user object renamed to account
  - downstream deployed a 'non-breaking' change
- code excerpt:
```js
const response = await axios.get('/users/me')
const userId = response.data.user.id  // user renamed to account
```
- reproduction:
1. Call /users/me after downstream schema change
2. Observe TypeError on response.data.user
