# IN-015: Dead Letter Queue Full Causes New Messages To Be Rejected

## User Prompt

Our message queue is backing up and publishers are being rejected. The main consumer is running correctly. What is causing the backpressure?

## Context Provided To The Skill

- stack: Node.js 20.11, amqplib 0.10, RabbitMQ 3.12
- environment: production
- logs:
- new messages rejected with NACK from broker
  - orders.dlq queue has x-max-length: 1000 and is at 1000 messages
  - messages failing validation are nacked to DLQ
  - DLQ has been full for 3 days — never consumed
  - main queue now backing up as publishers receive rejection
- code excerpt:
```js
// Consumer
channel.consume(mainQueue, (msg) => {
  if (!isValid(msg)) {
    channel.nack(msg, false, false)  // sends to DLQ
    return
  }
  process(msg)
  channel.ack(msg)
})
// No DLQ consumer running
```
- reproduction:
1. Invalid messages accumulate in DLQ
2. DLQ reaches x-max-length limit (1000)
3. New nacks rejected by broker (no space in DLQ)
4. Main queue backs up
