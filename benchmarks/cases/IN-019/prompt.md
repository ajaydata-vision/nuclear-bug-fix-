# IN-019: Third-Party API Rate Limit Exceeded Causing Cascading Service Failures

## User Prompt

When our payment API rate limit is exceeded the entire payment service falls over. We have retry logic but it makes things worse. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, external payment API
- environment: production under peak load
- logs:
- payment API returns 429 Too Many Requests
  - all requests retried immediately on 429
  - retry storm amplifies load on payment API
  - entire payment service becomes unavailable
- code excerpt:
```js
async function callPaymentAPI(data) {
  const result = await axios.post(PAYMENT_API, data)
  if (result.status === 429) {
    return callPaymentAPI(data)  // immediate retry — no backoff
  }
  return result
}
```
- reproduction:
1. Exceed payment API rate limit
2. All callers immediately retry
3. Retry storm further saturates the API
4. Payment service completely unavailable
