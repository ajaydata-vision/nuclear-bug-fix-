# RC-017: Parallel Async Operations Snapshot Shared State Across Await Causing Silent Data Corruption

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
  - each aggregation snapshots the shared total before an async audit call
  - category-level sums are correct; only the final total is sometimes low
- code excerpt:
```js
const result = { total: 0, categories: {} }

await Promise.all(categories.map(async (cat) => {
  const sum = await db.sumCategory(cat)
  const currentTotal = result.total
  await audit.logCategoryTotal(cat, sum)
  result.total = currentTotal + sum
  result.categories[cat] = sum
}))
```
- reproduction:
1. Run report with 5 categories in parallel via Promise.all
2. Each async operation snapshots result.total into currentTotal
3. The async audit call yields; other tasks update result.total while this task is suspended
4. When the original task resumes, it writes back a stale currentTotal + sum
5. Final total is less than actual sum
