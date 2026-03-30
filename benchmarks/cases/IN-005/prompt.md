# IN-005: Message Acknowledged Before Processing And Lost On Handler Failure

## User Prompt

Orders are sometimes silently dropped when our message consumer encounters an error. The queue shows zero unprocessed messages but some orders are missing. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, amqplib 0.10, RabbitMQ 3.12
- environment: production
- logs:
- messages consumed from queue
  - order processing sometimes incomplete
  - no dead-letter entries
  - message acknowledged before processOrder() completes
  - if processOrder() throws, message is not retried
- code excerpt:
```js
channel.consume(queue, async (msg) => {
  channel.ack(msg)  // acknowledged before processing
  await processOrder(JSON.parse(msg.content))
})
```
- reproduction:
1. Consume message
2. Acknowledge immediately
3. processOrder() throws an error
4. Observe message not retried — lost
