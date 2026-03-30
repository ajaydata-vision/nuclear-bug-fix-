# IN-011: Events Not Propagating Because Event Bus Topic Name Mismatch

## User Prompt

Events are being published to our event bus but the downstream consumers never receive them. No errors in publishing. What is wrong?

## Context Provided To The Skill

- stack: Node.js 20.11, AWS EventBridge
- environment: production
- logs:
- events published successfully to event bus
  - downstream consumer never triggered
  - publisher uses source: 'com.example.orders'
  - consumer rule matches source: 'com.example.order' (missing 's')
  - EventBridge shows events published but zero matched rules
- code excerpt:
```js
// Publisher
eventbridge.putEvents({ Entries: [{ Source: 'com.example.orders', ... }] })

// Consumer rule
{ "source": ["com.example.order"] }  // typo
```
- reproduction:
1. Publish event with source com.example.orders
2. Consumer rule does not match
3. Zero events routed to consumer
