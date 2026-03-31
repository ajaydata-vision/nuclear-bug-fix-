# BI-001: First WhatsApp Event Lost During Startup Handshake

## User Prompt

Our Python app launches the Node WhatsApp bridge and marks it "connected" as
soon as the subprocess starts. Most messages arrive fine, but the first inbound
message after startup is often missing. If a second message arrives later, that
one appears. What is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 + Node 20.11.0 + `@whiskeysockets/baileys` 6.7.5
- versions: websocket relay from Node bridge to Python app
- environment: source run, local desktop app
- logs:
  - `[parent] spawned bridge pid=4824 at 10:00:01.102`
  - `[parent] listener attached at 10:00:02.404`
  - `[child] bridge_ready at 10:00:02.188`
  - `[child] first messages.upsert at 10:00:02.231 id=ABC123`
  - first inbound WhatsApp message never appears in UI
- code excerpt:

```python
proc = await asyncio.create_subprocess_exec("node", "wa_bridge.js", stdout=PIPE)
self.bridge_state = "connected"
asyncio.create_task(self._read_bridge_stdout(proc.stdout))
```

- reproduction:
  1. Launch app
  2. Send one WhatsApp message immediately after QR/session restore
  3. First message is missing, later ones arrive
