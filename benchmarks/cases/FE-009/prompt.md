# FE-009: WebSocket Connects Before onmessage Handler Is Attached

## User Prompt

Our WebSocket sometimes misses the first message from the server after connecting. It only happens on fast connections. What is the bug?

## Context Provided To The Skill

- stack: React 18.2, native WebSocket API
- environment: browser
- logs:
- first message after connect sometimes not received
  - subsequent messages received correctly
  - no errors in console
  - only reproducible on fast connections
- code excerpt:
```js
const ws = new WebSocket(url)
setTimeout(() => {
  ws.onmessage = (e) => handleMessage(e.data)
}, 0)
```
- reproduction:
1. Connect on fast network
2. Server sends message immediately on connect
3. Observe first message occasionally missed
