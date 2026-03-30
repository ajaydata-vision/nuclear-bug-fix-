# RC-005: Race Between WebSocket Message and HTTP Response Causes State Inconsistency

## User Prompt

Our collaborative document editor occasionally shows version conflicts when saving. The save API returns 200 but the UI sometimes shows an older version immediately after. What is the race condition?

## Context Provided To The Skill

- stack: Node.js 20.11, Socket.IO 4.6, Express 4.18.2
- environment: production
- logs:
- user updates document
  - POST /documents/:id returns 200
  - WebSocket broadcast fires before HTTP response reaches client
  - client receives WS event with new state before confirming HTTP save
  - UI shows version conflict
- code excerpt:
```js
app.post('/documents/:id', async (req, res) => {
  await db.update(req.params.id, req.body)
  io.emit('document:updated', { id: req.params.id })  // fires before res.json
  res.json({ success: true })
})
```
- reproduction:
1. Client posts document update
2. Server broadcasts WS event before HTTP response
3. Other clients receive new state before originator confirms save
4. Race between WS and HTTP causes version conflict on originating client
