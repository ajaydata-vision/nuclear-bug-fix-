# RC-016: WebSocket Reconnect Creates Duplicate Event Listeners Causing Double Processing

## User Prompt

Users see duplicate notifications after any network disruption. The number of duplicates matches how many times the WebSocket reconnected. What is causing this?

## Context Provided To The Skill

- stack: React 18.2, native WebSocket API
- environment: browser SPA with auto-reconnect
- logs:
- notifications appear multiple times after network disruptions
  - count of duplicate notifications equals number of reconnect cycles
  - DevTools shows multiple onmessage handlers on the same WebSocket
  - reconnect adds new handler without removing the old one
- code excerpt:
```js
function reconnect() {
  ws = new WebSocket(url)
  ws.onmessage = handleMessage  // previous ws handlers not cleaned up
  ws.onclose = () => setTimeout(reconnect, 1000)
}
```
- reproduction:
1. Connect WebSocket
2. Simulate network drop → reconnect
3. Receive a notification
4. Observe notification displayed twice (once per connection cycle)
