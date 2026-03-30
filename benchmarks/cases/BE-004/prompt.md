# BE-004: Client Gets Timeout But Operation Completed Server-Side

## User Prompt

Our report generation endpoint times out for the client but the operation actually completes. Retrying creates duplicate records. What is the real bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, PostgreSQL 16.1
- environment: production behind load balancer with 30s timeout
- logs:
- client receives 504 Gateway Timeout after 30 seconds
  - server logs show operation completing successfully at 31 seconds
  - database has the created record
  - retrying the request creates duplicate records
- code excerpt:
```js
app.post('/reports', async (req, res) => {
  const report = await generateReport(req.body) // takes 31 seconds
  await db.reports.create(report)
  res.json(report)
})
```
- reproduction:
1. POST /reports with large dataset
2. Client receives 504 after 30s
3. Check DB — report exists
4. Retry request — duplicate report created
