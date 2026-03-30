# IN-006: Consumer Lag Grows Because DB Query Inside Handler Is Bottleneck

## User Prompt

Our Kafka consumer is falling behind the producer despite having enough CPU and memory. Consumer lag keeps growing. What is the real bottleneck?

## Context Provided To The Skill

- stack: Node.js 20.11, KafkaJS 2.2, PostgreSQL 16.1
- environment: production under load
- logs:
- Kafka consumer lag growing continuously
  - consumer processing ~100 msg/s, producer ~500 msg/s
  - each message triggers: SELECT * FROM products WHERE id = ?
  - query takes 200ms each
  - no query caching or batching
- code excerpt:
```js
consumer.run({
  eachMessage: async ({ message }) => {
    const order = JSON.parse(message.value)
    const product = await db.query('SELECT * FROM products WHERE id = $1', [order.productId])
    await processOrder(order, product.rows[0])
  }
})
```
- reproduction:
1. Run consumer under 500 msg/s load
2. Monitor consumer lag over 10 minutes
3. Observe lag growing continuously
