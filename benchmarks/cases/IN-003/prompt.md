# IN-003: Webhook Processed Twice Because Retry Not Deduplicated

## User Prompt

Our webhook handler sometimes creates duplicate orders when the provider retries delivery. The events have the same ID but we process them twice. What is the real bug?

## Context Provided To The Skill

- stack: Node.js 20.11, Express 4.18.2, PostgreSQL 16.1
- environment: production
- logs:
- order.created webhook received twice
  - same event ID in both deliveries
  - first delivery took 4500ms (near timeout)
  - provider retried after 5000ms timeout
  - duplicate order created in database
- code excerpt:
```js
app.post('/webhooks', async (req, res) => {
  const event = req.body
  await createOrder(event.data)  // no idempotency check
  res.sendStatus(200)
})
```
- reproduction:
1. Webhook delivery takes >5 seconds (timeout)
2. Provider retries the same event
3. Observe duplicate order created
