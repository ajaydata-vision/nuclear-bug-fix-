# BI-002: Duplicate Delivery After Bridge Reconnect

## User Prompt

After the WhatsApp bridge reconnects a couple of times, every inbound message is
handled two or three times. A fresh app launch is fine. The duplication always
starts after reconnect. What is actually wrong?

## Context Provided To The Skill

- stack: Node 20.11.0 + `@whiskeysockets/baileys` 6.7.5 + Python parent app
- versions: websocket relay from Node bridge
- environment: source run, local desktop app
- logs:
  - first session: one inbound message -> one UI event
  - after second reconnect: same inbound message ID forwarded 3 times
  - reconnect count increments each time network drops
- code excerpt:

```js
async function connectBridge() {
  const sock = makeWASocket({ auth: state });

  sock.ev.on("connection.update", ({ connection }) => {
    if (connection === "close") {
      connectBridge();
    }
  });

  sock.ev.on("messages.upsert", forwardMessage);
}
```

- reproduction:
  1. Start bridge
  2. Force two reconnect cycles
  3. Send one inbound message
  4. Observe duplicate deliveries
