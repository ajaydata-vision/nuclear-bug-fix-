# IN-015: Dead Letter Queue Full With reject-publish Overflow Causes New Messages To Be Rejected

## User Prompt

Our message queue is backing up and publishers are being rejected. The main consumer is running correctly. What is causing the backpressure?

## Context Provided To The Skill

- stack: Node.js 20.11, amqplib 0.10, RabbitMQ 3.12
- environment: production
- logs:
  - broker reports dead-letter publish rejected
  - orders.dlq queue has x-max-length: 1000, x-overflow: reject-publish, and is at 1000 messages
  - messages failing validation are nacked to DLQ
  - DLQ has been full for 3 days and is never consumed
  - main queue now backs up as dead-lettering failures accumulate
- code excerpt:
```js
await channel.assertQueue('orders.dlq', {
  durable: true,
  arguments: {
    'x-max-length': 1000,
    'x-overflow': 'reject-publish'
  }
})

channel.consume(mainQueue, (msg) => {
  if (!isValid(msg)) {
    channel.nack(msg, false, false)  // dead-letters to orders.dlq
    return
  }
  process(msg)
  channel.ack(msg)
})
// No DLQ consumer running
```
- reproduction:
1. Invalid messages accumulate in DLQ
2. DLQ reaches x-max-length limit (1000) with overflow set to reject-publish
3. New dead-letter attempts are rejected by the broker because the DLQ will not accept more messages
4. Main queue backs up
