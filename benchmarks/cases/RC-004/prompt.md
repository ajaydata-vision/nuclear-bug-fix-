# RC-004: Cache Stampede Under High Load Overwhelms Database

## User Prompt

Our database gets overwhelmed every hour at exactly the same time. The load is otherwise manageable. Redis caching is in place. What is causing the periodic spike?

## Context Provided To The Skill

- stack: Node.js 20.11, Redis 7.2, PostgreSQL 16.1
- environment: production under high traffic
- logs:
- database CPU spikes to 100% every hour
  - spike duration matches Redis TTL expiry time
  - hundreds of concurrent queries for the same key
  - Redis cache miss triggers immediate DB query for all concurrent waiters
- code excerpt:
```js
async function getPopularData(key) {
  const cached = await redis.get(key)
  if (!cached) {
    const data = await db.query(expensiveQuery)  // all callers hit DB simultaneously
    await redis.setex(key, 3600, JSON.stringify(data))
    return data
  }
  return JSON.parse(cached)
}
```
- reproduction:
1. Wait for cache key to expire (after 1 hour)
2. Observe all concurrent requests hitting DB simultaneously
3. Database CPU spikes
