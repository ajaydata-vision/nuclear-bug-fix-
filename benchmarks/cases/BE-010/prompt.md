# BE-010: Background Job Consumed But Silently Disappears On Error

## User Prompt

Email background jobs are consumed from our queue but emails are never sent and no failures appear in the dashboard. Jobs just disappear. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, BullMQ 5.0, Redis 7.2
- environment: production
- logs:
- email sending jobs consumed from queue
  - emails not delivered
  - job count goes to zero
  - no error logs
  - queue shows no failed jobs
- code excerpt:
```js
worker.on('active', async (job) => {
  try {
    await sendEmail(job.data)
  } catch (err) {
    console.log(err) // logged but not re-thrown
  }
})
```
- reproduction:
1. Queue an email job
2. Observe job consumed but email not sent
3. No failed job in queue
