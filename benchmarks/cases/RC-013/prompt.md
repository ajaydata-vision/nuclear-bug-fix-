# RC-013: Distributed Lock Acquired But Never Released After Process Crash

## User Prompt

Our report generation has been blocked for hours. Redis shows a lock key that never expires. The process that set it crashed. How do we fix this and prevent it recurring?

## Context Provided To The Skill

- stack: Node.js 20.11, Redis 7.2
- environment: production
- logs:
- lock key lock:report exists in Redis with no TTL
  - process that acquired the lock crashed
  - all subsequent lock acquisition attempts time out
  - lock key never expires
  - report generation completely blocked
- code excerpt:
```js
const acquired = await redis.setnx('lock:report', '1')
if (acquired) {
  await generateReport()
  await redis.del('lock:report')  // never reached if crash occurs
}
```
- reproduction:
1. Acquire lock
2. Process crashes during generateReport()
3. Lock key persists forever with no TTL
4. All subsequent attempts fail — permanently blocked
