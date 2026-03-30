# BE-003: Duplicate Write From Retries Without Idempotency

## User Prompt

Our `POST /orders` endpoint sometimes creates two orders for one checkout click.
The frontend only sends one request in normal cases, but when the network is
slow we see duplicate rows and duplicate confirmation emails. Where is the real
bug?

## Context Provided To The Skill

- stack: Node.js 20.11.0 + Express 4.18.2 + PostgreSQL 16.1
- versions: Nginx in front of the app
- environment: production behind a retrying mobile client
- logs:
  - same client request payload appears twice within 2 seconds
  - both requests return `201 Created`
  - order table contains two rows with different IDs and same checkout payload
- code excerpt:

```js
app.post('/orders', async (req, res) => {
  const order = await db.order.create({ data: req.body });
  await sendConfirmation(order.id);
  res.status(201).json(order);
});
```

- reproduction:
  1. Simulate client timeout and retry
  2. Send same order payload twice
  3. Observe two persisted orders
