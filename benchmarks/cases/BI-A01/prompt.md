# BI-A01: Bridge Output Stops Parsing After Diagnostics

## User Prompt

Our Python desktop app spawns a Node bridge for WhatsApp events. After we added
extra diagnostics, the parent started failing while decoding some child output,
and the bridge dies after a few events. Where is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 parent + Node 20.11.0 child bridge
- versions: `@whiskeysockets/baileys` 6.7.5
- environment: source run on Windows 11
- logs:
  - parent reads child stdout line by line and decodes JSON frames
  - attached `assets/stdout-capture.txt` shows raw child output around the failure
- code excerpt:

```js
function emitFrame(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}

function debug(...args) {
  console.log("[bridge]", ...args);
}

sock.ev.on("messages.upsert", ({ messages }) => {
  debug("ack", messages[0].key.id);
  emitFrame({ type: "message", id: messages[0].key.id });
});
```

- reproduction:
  1. Start bridge
  2. Receive several WhatsApp events
  3. Parent eventually fails to parse one stdout line
