# IN-007: Duplicate Order Created From At-Least-Once Message Delivery

## User Prompt

We see duplicate orders in our database that correlate with consumer restarts. The consumer processes each message only once during normal operation. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, KafkaJS 2.2, PostgreSQL 16.1
- environment: production
- logs:
- duplicate orders appearing in database
  - correlates with consumer restarts
  - same correlation_id in both order records
  - message offset committed after processing but consumer crashed before commit
- code excerpt:
```js
await processOrder(order)
// Consumer crashes here before offset commit
await commitOffset()
```
- reproduction:
1. Consumer processes message and creates order
2. Consumer crashes before offset commit
3. Consumer restarts and reprocesses same message
4. Duplicate order created
