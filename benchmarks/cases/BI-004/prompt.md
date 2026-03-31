# BI-004: Packaged App Uses A Different Protocol Version Than The Child Bridge

## User Prompt

The desktop app can talk to the WhatsApp bridge in development, but in the
packaged build the parent says the child is "connected" while messages stop
flowing after startup. The logs show the parent and child are not on the same
build version. Where is the real bug?

## Context Provided To The Skill

- stack: Python 3.11.8 parent + Node 20.11.0 child bridge + qasync UI
- versions: packaged Windows build, source works
- environment: packaged `.exe` only
- logs:
  - `[parent] version=1.4.1 bridge_protocol=3`
  - `[child] version=1.4.0 bridge_protocol=2`
  - `[bridge] handshake accepted`
  - `[bridge] no further events received`
- code excerpt:

```python
async def start_bridge(self):
    proc = await asyncio.create_subprocess_exec("node", str(self.bridge_script))
    self.bridge_state = "connected"
    await self._read_bridge_stdout(proc.stdout)
```

- reproduction:
  1. Launch packaged app
  2. Open WhatsApp panel
  3. Messages stop after initial handshake
