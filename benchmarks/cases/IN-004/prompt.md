# IN-004: Queue Consumer Never Receives Messages Due To Topic Name Typo

## User Prompt

Our Kafka consumer never receives messages even though the producer is sending successfully. No errors in either producer or consumer. What is the bug?

## Context Provided To The Skill

- stack: Node.js 20.11, KafkaJS 2.2, Kafka cluster
- environment: production
- logs:
- producer sends messages successfully to orders.created
  - consumer receives zero messages
  - consumer subscribed to order.created (missing 's')
  - both topics exist in Kafka (auto-create enabled)
- code excerpt:
```js
// Producer
await producer.send({ topic: 'orders.created', messages: [msg] })

// Consumer
await consumer.subscribe({ topic: 'order.created' }) // typo: missing 's'
```
- reproduction:
1. Publish message to orders.created
2. Consumer receives nothing
3. Check Kafka topics — both orders.created and order.created exist with different message counts
