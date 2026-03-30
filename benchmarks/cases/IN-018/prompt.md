# IN-018: Database Connection Pool Exhausted Under Load Causing Request Timeouts

## User Prompt

Under load our API times out randomly. Database connections seem to be the bottleneck. What is the actual problem and how do we fix it?

## Context Provided To The Skill

- stack: Node.js 20.11, pg (node-postgres) 8.11, PostgreSQL 16.1
- environment: production under load
- logs:
- requests time out after 30 seconds under load
  - pg pool queue length grows continuously
  - pool size: 10 connections
  - each request holds a connection for the entire request lifecycle
  - slow queries holding connections for 5-10 seconds each
- code excerpt:
```js
const pool = new Pool({ max: 10 })

app.get('/report', async (req, res) => {
  const client = await pool.connect()
  const data = await client.query(expensiveQuery)  // 8 second query
  // connection held for 8 seconds
  res.json(data.rows)
  client.release()
})
```
- reproduction:
1. Send 15 concurrent requests to /report
2. Each holds a connection for 8 seconds
3. Pool of 10 exhausted; request 11+ times out waiting
