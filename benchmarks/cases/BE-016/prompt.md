# BE-016: Legitimate Users Hit Rate Limit Because Proxy IP Used As Key

## User Prompt

All users hit the rate limit simultaneously as if they share the same IP address. Rate limiting is configured correctly for individual IPs. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, express-rate-limit 7.0, Nginx proxy
- environment: production behind Nginx reverse proxy
- logs:
- all users hit rate limit simultaneously
  - rate limit key is req.ip
  - req.ip shows Nginx proxy IP (127.0.0.1) for all requests
  - X-Forwarded-For header contains real client IPs
- code excerpt:
```js
const limiter = rateLimit({
  keyGenerator: (req) => req.ip
})
```
- reproduction:
1. Multiple users make requests
2. All hit rate limit at the same time
3. Log req.ip — all show 127.0.0.1
