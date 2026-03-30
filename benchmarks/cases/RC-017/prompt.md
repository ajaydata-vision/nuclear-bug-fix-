# RC-017: Parallel Async Operations Race On Shared Object Causing Silent Data Corruption

## User Prompt

Our financial report totals are wrong under load but always correct when run sequentially. We use Promise.all for performance. What is the subtle bug?

## Context Provided To The Skill

- stack: Node.js 20.11, TypeScript 5.0
- environment: backend service processing concurrent requests
- logs:
- report totals occasionally wrong under concurrent load
  - no errors thrown
  - totals correct under single-threaded sequential processing
  - Promise.all used to run category aggregations in parallel
  - all aggregations write to the same shared result object
- code excerpt:
```js
const result = { total: 0, categories: {} }

await Promise.all(categories.map(async (cat) => {
  const sum = await db.sumCategory(cat)
  result.total += sum           // race: read-modify-write on shared object
  result.categories[cat] = sum
}))
```
- reproduction:
1. Run report with 5 categories in parallel via Promise.all
2. Each async operation reads result.total, adds its sum, writes back
3. Concurrent read-modify-writes lose updates
4. Final total is less than actual sum
