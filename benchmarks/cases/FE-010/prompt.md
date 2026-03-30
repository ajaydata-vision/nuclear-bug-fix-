# FE-010: WebSocket Reconnect Loop From Auth Close Code Ignored

## User Prompt

Our WebSocket goes into an infinite reconnect loop instead of showing an auth error to the user. The close event always triggers reconnect. What is the real bug?

## Context Provided To The Skill

- stack: React 18.2, native WebSocket API
- environment: browser
- logs:
- WebSocket connects
  - immediately closes with code 4001 (auth error)
  - reconnects automatically
  - closes again with 4001
  - loop continues indefinitely
  - network tab shows constant connect/disconnect cycle
- code excerpt:
```js
ws.onclose = () => {
  setTimeout(() => reconnect(), 1000)
}
```
- reproduction:
1. Let auth token expire
2. Observe WebSocket connection cycling every second indefinitely
