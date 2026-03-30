# BE-011: Cron Job Runs At Wrong Time Because Server Timezone Is Not UTC

## User Prompt

Our daily report cron runs at the wrong time in production. It is set to 21:00 but runs at a different time. Local testing is correct. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, node-cron 3.0
- environment: production server in UTC+5:30 timezone
- logs:
- cron job runs at 02:30 local time instead of 21:00 UTC
  - server timezone: Asia/Kolkata (UTC+5:30)
  - cron expression: 0 21 * * *
- code excerpt:
```js
cron.schedule('0 21 * * *', runDailyReport)
```
- reproduction:
1. Deploy to server with IST timezone
2. Observe report runs at 21:00 IST (15:30 UTC) not 21:00 UTC
