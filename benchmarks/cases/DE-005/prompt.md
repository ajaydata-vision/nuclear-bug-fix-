# DE-005: TLS Certificate Expired Causing API Failures With Cryptic SSL Error

## User Prompt

All our API calls started failing at midnight with a certificate error. Code has not changed. What happened and how do we fix it?

## Context Provided To The Skill

- stack: Node.js 20.11, axios 1.6, HTTPS API
- environment: production
- logs:
- Error: certificate has expired
  - CERT_HAS_EXPIRED code
  - started at midnight UTC
  - affects all HTTPS calls to api.example.com
  - curl -v shows NotAfter: Jan 15 00:00:00 2026 GMT
- code excerpt:
```js
await axios.get('https://api.example.com/data')
// Error: certificate has expired (CERT_HAS_EXPIRED)
```
- reproduction:
1. Make any HTTPS request to api.example.com after the cert expiry date
2. Observe CERT_HAS_EXPIRED error
