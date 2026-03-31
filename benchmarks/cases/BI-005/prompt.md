# BI-005: Realtime Event Is Emitted Before The Listener Exists

## User Prompt

Our Python app receives realtime WhatsApp updates through a Node bridge. On
slow machines the first event after connect is often missed, but later events
arrive normally. The logs show the event was emitted before the Python listener
was attached. What is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 parent + Node 20.11.0 child bridge + websockets 12.0
- versions: Windows 11 desktop app
- environment: source run
- logs:
  - `[parent] spawn=10:03:01.102`
  - `[child] ready=10:03:01.733`
  - `[child] first_event=10:03:01.744`
  - `[parent] listener_attached=10:03:01.981`
- code excerpt:

```python
proc = await asyncio.create_subprocess_exec("node", "wa_bridge.js")
asyncio.create_task(self._read_stdout(proc.stdout))
self.bridge_ready = True
```

- reproduction:
  1. Launch the app on a slow machine or VM
  2. Connect the WhatsApp session
  3. Observe the first event is missed, later ones arrive
