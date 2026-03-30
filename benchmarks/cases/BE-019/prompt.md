# BE-019: Stale Cache Returned After Write Because Invalidation Never Happens

## User Prompt

Product data shows old values immediately after an update. The update API returns 200 and the database has the new data. The issue resolves after an hour. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, Redis 7.2
- environment: production
- logs:
- PUT /products/:id returns 200
  - GET /products/:id returns old data
  - Redis cache TTL is 1 hour
  - correct data visible after cache TTL expires
- code excerpt:
```js
async function getProduct(id) {
  const cached = await redis.get(`product:${id}`)
  if (cached) return JSON.parse(cached)
  const product = await db.products.findById(id)
  await redis.setex(`product:${id}`, 3600, JSON.stringify(product))
  return product
}

async function updateProduct(id, data) {
  await db.products.update(id, data)
  // cache not invalidated
}
```
- reproduction:
1. GET /products/1 → cached
2. PUT /products/1 with updated data
3. GET /products/1 → returns stale cached data
