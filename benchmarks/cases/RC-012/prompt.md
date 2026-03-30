# RC-012: Race In Batch Processing Causes Duplicate Charges

## User Prompt

Our subscription billing worker is creating duplicate charges when multiple workers run simultaneously. How do we prevent the same subscription from being charged twice?

## Context Provided To The Skill

- stack: Node.js 20.11, PostgreSQL 16.1, BullMQ 5.0
- environment: production with 3 worker instances
- logs:
- duplicate charges for some subscription renewals
  - two workers processing same subscription simultaneously
  - subscription status check: both see status='active' before either charges
  - both charge and update to 'charged'
- code excerpt:
```js
// Each worker:
const sub = await db.subscriptions.findOne({ where: { status: 'active', dueDate: now } })
if (sub) {
  await charge(sub)
  await sub.update({ status: 'charged' })
}
```
- reproduction:
1. Three workers process batch simultaneously
2. All three find same subscription as 'active'
3. All three charge → duplicate charges
